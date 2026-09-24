import hashlib
import re
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "The Guardian World": "https://www.theguardian.com/world/rss",
}


def _make_id(link: str) -> str:
    return hashlib.sha256(link.encode()).hexdigest()[:16]


def _parse_date(entry) -> str:
    for field in ("published", "updated", "created"):
        raw = entry.get(field)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                return dt.isoformat()
            except Exception:
                pass
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(raw)
                return dt.isoformat()
            except Exception:
                pass
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if time_struct:
        try:
            dt = datetime(*time_struct[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat()


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip() if text else ""


def fetch_feed(source_name: str, url: str) -> list[dict]:
    logger.info("Fetching feed: %s (%s)", source_name, url)
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        logger.warning("Feed %s returned an error: %s", source_name, feed.bozo_exception)
        return []

    articles = []
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue

        summary = _clean_html(
            entry.get("summary", "")
            or entry.get("description", "")
            or entry.get("content", [{}])[0].get("value", "")
            if entry.get("content")
            else ""
        )

        articles.append({
            "id": _make_id(link),
            "title": entry.get("title", "Untitled"),
            "summary": summary,
            "link": link,
            "published": _parse_date(entry),
            "source": source_name,
        })

    logger.info("Fetched %d articles from %s", len(articles), source_name)
    return articles


def fetch_all_feeds() -> list[dict]:
    all_articles = []
    for source_name, url in RSS_FEEDS.items():
        try:
            articles = fetch_feed(source_name, url)
            all_articles.extend(articles)
        except Exception as e:
            logger.error("Failed to fetch %s: %s", source_name, e)
    return all_articles
