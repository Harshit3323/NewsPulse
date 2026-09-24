import re
import logging
from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "it", "its", "this", "that", "these", "those", "he", "she", "they",
    "we", "you", "i", "me", "my", "his", "her", "our", "your", "their",
    "not", "no", "nor", "if", "then", "else", "when", "where", "how",
    "what", "which", "who", "whom", "why", "so", "than", "too", "very",
    "just", "about", "above", "after", "again", "all", "also", "any",
    "because", "before", "between", "both", "each", "few", "more",
    "most", "other", "some", "such", "into", "over", "own", "same",
    "through", "under", "up", "down", "out", "off", "only", "now",
    "news", "says", "say", "said", "year", "years", "old", "people",
    "world", "country", "countries", "new", "one", "two", "first",
    "time", "today", "live", "happened", "report", "reports",
    "according", "official", "officials", "president", "government",
    "minister", "state", "states", "major", "including", "told", "like",
    "many", "last", "back", "part", "another", "across", "around",
    "made", "make", "man", "woman", "men", "women", "day", "days",
    "week", "way", "home", "look", "long", "called", "think", "well",
    "still", "against", "amid",
}

DEFAULT_THRESHOLD = 4


def extract_keywords(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _cluster_label(keywords: Counter) -> str:
    most_common = keywords.most_common(3)
    return " / ".join(word for word, _ in most_common)


def cluster_articles(articles: list[dict], threshold: int = DEFAULT_THRESHOLD) -> list[dict]:
    clusters: list[dict] = []

    for article in articles:
        text = f"{article['title']} {article['summary']}"
        keywords = extract_keywords(text)

        assigned = False
        for cluster in clusters:
            overlaps = [keywords & member_keywords for member_keywords in cluster["member_keywords"]]
            if any(len(overlap) >= threshold for overlap in overlaps):
                cluster["article_ids"].append(article["id"])
                cluster["keywords"].update(keywords)
                cluster["all_keywords"].update(keywords)
                cluster["member_keywords"].append(keywords)
                assigned = True
                break

        if not assigned:
            clusters.append({
                "keywords": set(keywords),
                "all_keywords": Counter(keywords),
                "member_keywords": [keywords],
                "article_ids": [article["id"]],
            })

    results = []
    for i, cluster in enumerate(clusters):
        article_ids = cluster["article_ids"]
        label = _cluster_label(cluster["all_keywords"])

        times = []
        for article in articles:
            if article["id"] in article_ids and article.get("published"):
                try:
                    times.append(datetime.fromisoformat(article["published"]))
                except (ValueError, TypeError):
                    pass

        start_time = min(times).isoformat() if times else ""
        end_time = max(times).isoformat() if times else ""

        results.append({
            "cluster_id": i + 1,
            "label": label,
            "article_ids": article_ids,
            "start_time": start_time,
            "end_time": end_time,
            "article_count": len(article_ids),
        })

    return results
