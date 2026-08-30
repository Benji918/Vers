import sqlite3
import re
import logging
from rapidfuzz import fuzz
from app.config import DATABASE_PATH
from app.data.books import BOOK_NAMES

logger = logging.getLogger("vers.matcher")

MIN_SEGMENT_WORDS = 3
CONFIDENCE_FLOOR = 0.35

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

def _score_candidates(sanitized: str, db_path: str, limit: int = 20) -> list:
    """
    Run the two-stage (FTS5 recall + rapidfuzz precision) pipeline and
    return ranked candidates. Each candidate is a dict with book/chapter/
    verse/text/confidence, sorted by score descending.
    """
    tokens = [t for t in sanitized.split() if len(t) > 1]
    if not tokens:
        return []

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
            LIMIT ?;
        """, (fts_query, limit))

        candidates = cursor.fetchall()
        if not candidates:
            return []

        scored = []
        for cand in candidates:
            cand_id, book_id, chapter, verse, text, rank = cand
            cand_clean = sanitize_transcript(text or "")
            score = fuzz.token_set_ratio(sanitized, cand_clean)
            scored.append({
                "book": BOOK_NAMES.get(book_id, f"Book {book_id}"),
                "chapter": chapter,
                "verse": verse,
                "text": text,
                "confidence": round(score / 100.0, 3),
                "score": score,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
    finally:
        conn.close()

def _split_segments(text: str) -> list[str]:
    """
    Split a continuous transcript into clause/sentence-sized segments so the
    matcher can identify multiple verses inside a long passage.
    """
    if not text:
        return []

    text = re.sub(r'\s+', ' ', text).strip()

    raw_parts = re.split(r'(?<=[.!?;])\s+', text)

    segments = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue

        if len(part.split()) > 14:
            for sub in re.split(r'[,:]\s+', part):
                sub = sub.strip()
                if sub and len(sub.split()) >= MIN_SEGMENT_WORDS:
                    segments.append(sub)
        else:
            segments.append(part)

    long = [s for s in segments if len(s.split()) >= MIN_SEGMENT_WORDS]
    return long if long else [text]

def find_verse(transcript: str, db_path: str = DATABASE_PATH) -> dict | None:
    """
    Return the single best matching verse for a transcript.
    """
    sanitized = sanitize_transcript(transcript)
    if not sanitized:
        return None

    scored = _score_candidates(sanitized, db_path)
    if not scored:
        logger.info(f"No candidates for query: {transcript}")
        return None

    top = scored[0]
    logger.info(
        f"Matched '{transcript}' -> {top['book']} {top['chapter']}:{top['verse']} "
        f"(score: {top['confidence']})"
    )
    return {k: top[k] for k in ("book", "chapter", "verse", "text", "confidence")}

def find_verses(transcript: str, db_path: str = DATABASE_PATH, max_results: int = 6) -> dict | None:
    """
    Identify one or more verses from a (possibly long) transcript.

    The transcript is split into clause-sized segments; each segment is
    matched independently, then the matches are grouped by book/chapter.
    Contiguous verses within the dominant chapter are returned as a range
    (e.g. Psalms 23:1-5), so reading a whole passage surfaces every verse.

    Returns:
        {
          "type": "match",
          "book": "Psalms",
          "chapter": 23,
          "verses": [ {"chapter", "verse", "text", "confidence"}, ... ],
          "range": {"start": 1, "end": 5},   # None for a single verse
          "query": <original text>
        }
        or None when nothing matches.
    """
    raw = (transcript or "").strip()
    if not raw:
        return None

    anchor = find_verse(raw, db_path)
    anchor_bc = (anchor["book"], anchor["chapter"]) if anchor else None

    matched_by_key: dict[tuple, dict] = {}

    for segment in _split_segments(raw):
        sanitized = sanitize_transcript(segment)
        if not sanitized:
            continue
        scored = _score_candidates(sanitized, db_path, limit=8)
        if not scored:
            continue

        top = scored[0]

        if anchor_bc:
            anchor_candidates = [c for c in scored if (c["book"], c["chapter"]) == anchor_bc]
            if anchor_candidates:
                anchor_candidate = anchor_candidates[0]
                if (top["book"], top["chapter"]) != anchor_bc and anchor_candidate["confidence"] >= CONFIDENCE_FLOOR:
                    top = anchor_candidate

        if top["confidence"] < CONFIDENCE_FLOOR:
            continue

        key = (top["book"], top["chapter"], top["verse"])
        record = {
            "book": top["book"],
            "chapter": top["chapter"],
            "verse": top["verse"],
            "text": top["text"],
            "confidence": top["confidence"],
        }
        if key in matched_by_key:
            prev = matched_by_key[key]
            if record["confidence"] > prev["confidence"]:
                matched_by_key[key] = record
        else:
            matched_by_key[key] = record

    if not matched_by_key:
        logger.info(f"No multi-verse match for query: {transcript}")
        anchor = find_verse(raw, db_path)
        if not anchor:
            return None
        return {
            "type": "match",
            "book": anchor["book"],
            "chapter": anchor["chapter"],
            "verses": [anchor],
            "range": None,
            "query": raw,
        }

    by_book_chapter: dict[tuple, list] = {}
    for record in matched_by_key.values():
        bc_key = (record["book"], record["chapter"])
        by_book_chapter.setdefault(bc_key, []).append(record)

    def group_score(records):
        n = len(records)
        total_conf = sum(r["confidence"] for r in records)
        span = max(r["verse"] for r in records) - min(r["verse"] for r in records) + 1
        return (n, total_conf, n / max(1, span))

    best_bc = max(by_book_chapter, key=lambda k: group_score(by_book_chapter[k]))
    best_records = sorted(by_book_chapter[best_bc], key=lambda r: r["verse"])
    best = best_records[:max_results]

    start = min(r["verse"] for r in best)
    end = max(r["verse"] for r in best)
    range_info = {"start": start, "end": end} if len(best) > 1 else None

    logger.info(
        f"Multi-verse matched '{transcript}' -> {best_bc[0]} {best_bc[1]}:"
        f"{start}-{end} (verses: {len(best)})"
    )

    return {
        "type": "match",
        "book": best_bc[0],
        "chapter": best_bc[1],
        "verses": best,
        "range": range_info,
        "query": raw,
    }