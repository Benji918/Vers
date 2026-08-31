import asyncio
import json
import logging
import websockets
from urllib.parse import urlencode
from app.config import DEEPGRAM_API_KEY, DEEPGRAM_MODEL, ENDPOINTING_MS, UTTERANCE_END_MS

logger = logging.getLogger("vers.deepgram")

AUDIO_ENCODING = "linear16"
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

class DeepgramStreamingClient:
    """
    Direct WebSocket client wrapper for Deepgram Streaming API (Nova-3).
    """
    def __init__(self, api_key: str = DEEPGRAM_API_KEY):
        self.api_key = api_key
        self.ws = None
        self._receive_task = None
        self.on_transcript = None
        self.is_connected = False

    async def connect(self, on_transcript_callback):
        """Establishes live WebSocket stream with Deepgram."""
        self.on_transcript = on_transcript_callback
        
        params = {
            "model": DEEPGRAM_MODEL,
            "encoding": AUDIO_ENCODING,
            "sample_rate": str(AUDIO_SAMPLE_RATE),
            "channels": str(AUDIO_CHANNELS),
            "interim_results": "true",
            "endpointing": str(ENDPOINTING_MS),
            "utterance_end_ms": str(UTTERANCE_END_MS),
            "smart_format": "true",
            "punctuate": "true"
        }
        
        ws_url = f"wss://api.deepgram.com/v1/listen?{urlencode(params)}"
        headers = {
            "Authorization": f"Token {self.api_key}"
        }

        try:
            self.ws = await websockets.connect(ws_url, additional_headers=headers)
            self.is_connected = True
            logger.info("Connected to Deepgram streaming endpoint")
            self._receive_task = asyncio.create_task(self._receiver_loop())
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            self.is_connected = False
            raise

    async def send_audio(self, chunk: bytes):
        """Pass-through binary audio frame to Deepgram."""
        if self.ws and self.is_connected:
            try:
                await self.ws.send(chunk)
            except Exception as e:
                logger.warning(f"Error sending audio chunk to Deepgram: {e}")

    async def _receiver_loop(self):
        """Listens for incoming transcript events and dispatches them."""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue

                if not isinstance(data, dict):
                    continue

                msg_type = data.get("type", "")
                
                if msg_type == "Results" or "channel" in data:
                    channel = data.get("channel") or {}
                    if not isinstance(channel, dict):
                        channel = {}
                    alternatives = channel.get("alternatives", [])
                    if isinstance(alternatives, list):
                        for alt in alternatives:
                            if not isinstance(alt, dict):
                                continue
                            transcript = alt.get("transcript", "").strip()
                            utterance_complete = bool(data.get("speech_final", False))
                            if transcript and self.on_transcript:
                                try:
                                    await self.on_transcript(transcript, utterance_complete)
                                except Exception:
                                    return
                            break
                            
                elif msg_type == "UtteranceEnd":
                    if self.on_transcript:
                        await self.on_transcript("", True)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Deepgram connection closed normally")
        except Exception as e:
            logger.error(f"Deepgram receiver exception: {e}", exc_info=True)
        finally:
            self.is_connected = False


    async def close(self):
        """Closes streaming connection cleanly."""
        self.is_connected = False
        if self.ws:
            try:
                await self.ws.send(json.dumps({"type": "CloseStream"}))
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
