import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.deepgram_client import DeepgramStreamingClient
from app.services.verse_matcher import find_verses
from app.config import DEEPGRAM_API_KEY

logger = logging.getLogger("vers.ws")
router = APIRouter()

@router.websocket("/ws/listen")
async def websocket_listen(websocket: WebSocket):
    """
    WebSocket endpoint for voice streaming and real-time verse identification.
    """
    await websocket.accept()
    logger.info("Client connected to /ws/listen")

    deepgram_client = DeepgramStreamingClient()

    async def on_deepgram_transcript(transcript: str, is_final: bool):
        """Callback invoked on Deepgram transcript events.

        For live streaming we only forward transcripts to the client so the
        user can read out long verses uninterrupted. The definitive verse
        match is computed once the client stops and sends the full
        accumulated text via a text_query message.
        """
        await websocket.send_json({
            "type": "transcript",
            "text": transcript,
            "is_final": is_final
        })

    try:
        if DEEPGRAM_API_KEY:
            try:
                await deepgram_client.connect(on_deepgram_transcript)
            except Exception as e:
                logger.warning(f"Could not connect to Deepgram: {e}")
        else:
            logger.warning("DEEPGRAM_API_KEY not set.")

        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                logger.info("Client disconnected from /ws/listen")
                break

            if "bytes" in message and message["bytes"]:
                await deepgram_client.send_audio(message["bytes"])
                
            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                    if payload.get("type") == "text_query":
                        query_text = payload.get("text", "")
                        matched = find_verses(query_text)
                        if matched:
                            await websocket.send_json({
                                "type": "match",
                                "book": matched["book"],
                                "chapter": matched["chapter"],
                                "verses": matched["verses"],
                                "range": matched["range"],
                                "query": query_text
                            })
                        else:
                            await websocket.send_json({
                                "type": "no_match",
                                "query": query_text,
                                "message": "No matching scripture found"
                            })
                except Exception as e:
                    logger.debug(f"Non-JSON text frame received: {e}")

    except WebSocketDisconnect:
        logger.info("Client disconnected from /ws/listen")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await deepgram_client.close()
