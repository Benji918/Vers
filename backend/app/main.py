import logging
import random
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import DATABASE_PATH
from app.db import init_fts5_index
from app.data.books import BOOK_NAMES
from app.websocket import router as ws_router
from app.services.verse_matcher import find_verse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("vers.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_fts5_index()
    yield

app = FastAPI(
    title="Vers Backend",
    description="Shazam for Bible Verses",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "app": "Vers",
        "status": "online",
        "description": "Voice-driven Bible verse identification"
    }

@app.get("/api/search")
async def search_verse(q: str):
    """Text-based verse lookup endpoint."""
    match = find_verse(q)
    if match:
        return {"found": True, "result": match}
    return {"found": False, "message": "No matching scripture found"}

@app.get("/api/samples")
async def sample_verses(n: int = 6):
    """Return a random selection of verses used as dynamic sample prompts."""
    try:
        conn = sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, book, chapter, verse, text FROM verses ORDER BY RANDOM() LIMIT ?;", (n,))
        rows = cursor.fetchall()
        conn.close()
        samples = [
            {
                "book": BOOK_NAMES.get(row["book"], f"Book {row['book']}"),
                "chapter": row["chapter"],
                "verse": row["verse"],
                "version": "KJV",
                "text": row["text"],
            }
            for row in rows
        ]
        return {"samples": samples}
    except Exception as e:
        logger.error(f"Failed to fetch sample verses: {e}")
        return {"samples": []}

@app.get("/health")
async def health_check():
    return {"status": "ok"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=9000, reload=True)