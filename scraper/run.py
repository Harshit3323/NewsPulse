import logging
from scraper.fetch import fetch_all_feeds
from scraper.extract import extract_articles
from scraper.cluster import cluster_articles
from scraper.db import (
    build_cluster,
    get_article_count,
    get_articles,
    get_cluster_count,
    get_db,
    init_db,
    insert_articles,
    replace_clusters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting News Pulse scraper")

    db = get_db()
    init_db(db)

    logger.info("Fetching articles from RSS feeds...")
    articles = fetch_all_feeds()
    logger.info("Fetched %d total articles", len(articles))

    logger.info("Extracting full article text...")
    articles = extract_articles(articles)

    logger.info("Saving articles to database...")
    new_count = insert_articles(db, articles)
    logger.info("Inserted %d new articles (out of %d fetched)", new_count, len(articles))

    logger.info("Clustering articles...")
    all_articles = get_articles(db)
    clusters = cluster_articles(all_articles)

    logger.info("Saving clusters to database...")
    cluster_documents = [
        build_cluster(
            label=cluster["label"],
            article_ids=cluster["article_ids"],
            start_time=cluster["start_time"],
            end_time=cluster["end_time"],
            cluster_id=cluster["cluster_id"],
        )
        for cluster in clusters
    ]
    replace_clusters(db, cluster_documents)

    total_articles = get_article_count(db)
    total_clusters = get_cluster_count(db)

    logger.info("Scraper run complete!")
    logger.info("Total articles in DB: %d", total_articles)
    logger.info("Total clusters in DB: %d", total_clusters)
    logger.info("New articles this run: %d", new_count)
    logger.info("Clusters stored after this run: %d", len(clusters))

    for cluster in clusters:
        logger.info("  Cluster %d: %s (%d articles)", cluster["cluster_id"], cluster["label"], cluster["article_count"])


if __name__ == "__main__":
    main()