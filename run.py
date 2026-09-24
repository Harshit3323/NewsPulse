import logging
from scraper.db import get_connection, init_db, insert_articles, insert_cluster
from scraper.fetch import fetch_all_feeds
from scraper.extract import extract_articles
from scraper.cluster import cluster_articles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== News Pulse Scraper — Starting ===")

    conn = get_connection()
    init_db(conn)

    articles = fetch_all_feeds()
    logger.info("Total articles fetched: %d", len(articles))

    articles = extract_articles(articles)

    new_count = insert_articles(conn, articles)
    logger.info("New articles inserted: %d (skipped duplicates)", len(articles) - new_count)

    clusters = cluster_articles(articles)
    for c in clusters:
        insert_cluster(conn, c["label"], c["article_ids"], c["start_time"], c["end_time"])
    logger.info("Clusters created: %d", len(clusters))

    total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    total_clusters = conn.execute("SELECT COUNT(*) FROM clusters").fetchone()[0]

    print("\n--- Summary ---")
    print(f"Articles fetched:      {len(articles)}")
    print(f"New articles inserted: {new_count}")
    print(f"Duplicates skipped:    {len(articles) - new_count}")
    print(f"Clusters created:      {len(clusters)}")
    print(f"Total articles in DB:  {total_articles}")
    print(f"Total clusters in DB:  {total_clusters}")

    conn.close()
    logger.info("=== News Pulse Scraper — Done ===")


if __name__ == "__main__":
    main()
