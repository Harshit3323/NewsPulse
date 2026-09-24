import logging
import trafilatura

logger = logging.getLogger(__name__)


def extract_full_text(url: str) -> str | None:
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            logger.warning("Could not download page: %s", url)
            return None
        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        logger.error("Extraction failed for %s: %s", url, e)
        return None


def extract_articles(articles: list[dict]) -> list[dict]:
    for article in articles:
        full_text = extract_full_text(article["link"])
        article["full_text"] = full_text or ""
        if not full_text:
            logger.warning("No text extracted for: %s", article["title"])
    return articles
