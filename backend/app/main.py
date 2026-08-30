import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_fts5_index
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=9000, reload=True)