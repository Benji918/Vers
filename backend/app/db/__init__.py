import sqlite3
import logging
import re
from app.config import DATABASE_PATH

logger = logging.getLogger("vers.db")

def clean_heading_noise(text: str) -> tuple[str, bool]:
    """
    Strip leading section-heading noise (e.g. leading paragraph ...Title... segment)
    from the copy going into the index without modifying the source table.
    """
    original = text
    cleaned = re.sub(r'^[#]+\s*', '', text)
    cleaned = re.sub(r'^\s*\[.*?\]\s*', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned, cleaned != original

def init_fts5_index(db_path: str = DATABASE_PATH) -> None:
    """
    Connects to SQLite db with raw sqlite3, creates external content FTS5
    virtual table 'verses_fts', and populates it if currently empty.
    Safe to run on every startup.
    """
    logger.info(f"Initializing FTS5 index on {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create external content FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(
                text, content='verses', content_rowid='id'
            );
        """)

        # Check if index is already populated
        cursor.execute("SELECT COUNT(*) FROM verses_fts;")
        count = cursor.fetchone()[0]

        if count == 0:
            logger.info("verses_fts is empty. Populating FTS5 index from verses table...")
            cursor.execute("SELECT id, text FROM verses;")
            rows = cursor.fetchall()
            
            cleaned_rows = []
            affected_count = 0
            for row_id, text in rows:
                cleaned_text, modified = clean_heading_noise(text or "")
                if modified:
                    affected_count += 1
                cleaned_rows.append((row_id, cleaned_text))

            cursor.executemany("INSERT INTO verses_fts(rowid, text) VALUES (?, ?);", cleaned_rows)
            cursor.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild');")
            conn.commit()
            logger.info(f"Successfully populated verses_fts with {len(cleaned_rows)} rows. Heading noise cleaned in {affected_count} rows.")
        else:
            logger.info(f"verses_fts already initialized with {count} rows. Skipping population.")
    except Exception as e:
        logger.error(f"Failed to initialize FTS5 index: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_fts5_index()
