import sqlite3
import re
import logging
from rapidfuzz import fuzz
from app.config import DATABASE_PATH
from app.data.books import BOOK_NAMES

logger = logging.getLogger("vers.matcher")

def sanitize_transcript(text: str) -> str:
    """
    Strip FTS5 special characters, lowercase, collapse whitespace.
    """
    if not text:
        return ""
    cleaned = re.sub(r'[\"\'\-\(\)\*\:\^\+\~\[\]\{\}\?\!\,\.\;\`]', ' ', text)
    cleaned = cleaned.lower()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def find_verse(transcript: str, db_path: str = DATABASE_PATH) -> dict | None:
    """
    Two-stage verse identification:
      - Stage 1 (Recall): Query FTS5 with sanitized tokens joined by OR, ordered by bm25() ASC (top 10).
      - Stage 2 (Precision): Re-rank shortlist using rapidfuzz token_sort_ratio against original verse texts.
    """
    sanitized = sanitize_transcript(transcript)
    tokens = [t for t in sanitized.split() if len(t) > 1]
    if not tokens:
        return None

    fts_query = " OR ".join(tokens)
    
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT v.id, v.book, v.chapter, v.verse, v.text, bm25(verses_fts) as rank
            FROM verses_fts
            JOIN verses v ON verses_fts.rowid = v.id
            WHERE verses_fts MATCH ?
            ORDER BY bm25(verses_fts) ASC
            LIMIT 10;
        """, (fts_query,))
        
        candidates = cursor.fetchall()
        if not candidates:
            logger.info(f"Stage 1 found 0 candidates for query: {transcript}")
            return None

        scored = []
        for cand in candidates:
            cand_id, book_id, chapter, verse, text, rank = cand
            cand_clean = sanitize_transcript(text or "")
            score = fuzz.token_sort_ratio(sanitized, cand_clean)
            scored.append((score, {
                "book": BOOK_NAMES.get(book_id, f"Book {book_id}"),
                "chapter": chapter,
                "verse": verse,
                "text": text,
                "confidence": round(score / 100.0, 3)
            }))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_match = scored[0][1]
        logger.info(f"Matched '{transcript}' -> {top_match['book']} {top_match['chapter']}:{top_match['verse']} (score: {top_match['confidence']})")
        return top_match

    except Exception as e:
        logger.error(f"Error during verse matching: {e}")
        return None
    finally:
        conn.close()
