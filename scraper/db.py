import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "news_pulse.db"


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            link TEXT NOT NULL,
            published TEXT,
            source TEXT,
            full_text TEXT
        );

        CREATE TABLE IF NOT EXISTS clusters (
            cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            article_ids TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            article_count INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()


def article_exists(conn: sqlite3.Connection, article_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM articles WHERE id = ?", (article_id,)).fetchone()
    return row is not None


def insert_article(conn: sqlite3.Connection, article: dict) -> bool:
    if article_exists(conn, article["id"]):
        return False
    conn.execute(
        "INSERT INTO articles (id, title, summary, link, published, source, full_text) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            article["id"],
            article["title"],
            article.get("summary", ""),
            article["link"],
            article.get("published", ""),
            article.get("source", ""),
            article.get("full_text", ""),
        ),
    )
    conn.commit()
    return True


def insert_articles(conn: sqlite3.Connection, articles: list[dict]) -> int:
    new_count = 0
    for article in articles:
        if insert_article(conn, article):
            new_count += 1
    return new_count


def insert_cluster(
    conn: sqlite3.Connection,
    label: str,
    article_ids: list[str],
    start_time: str,
    end_time: str,
) -> int:
    cursor = conn.execute(
        "INSERT INTO clusters (label, article_ids, start_time, end_time, article_count) "
        "VALUES (?, ?, ?, ?, ?)",
        (label, json.dumps(article_ids), start_time, end_time, len(article_ids)),
    )
    conn.commit()
    return cursor.lastrowid


def get_article_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]


def get_cluster_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM clusters").fetchone()[0]
