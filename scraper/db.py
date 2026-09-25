import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "news_pulse")


def get_db() -> Database:
    client = MongoClient(MONGODB_URI)
    return client[DB_NAME]


def init_db(db: Database) -> None:
    articles: Collection = db["articles"]
    clusters: Collection = db["clusters"]

    articles.create_index("id", unique=True)
    articles.create_index("published")
    articles.create_index("source")

    clusters.create_index("cluster_id", unique=True)
    clusters.create_index("article_ids")


def article_exists(db: Database, article_id: str) -> bool:
    return db["articles"].find_one({"id": article_id}) is not None


def insert_article(db: Database, article: dict) -> bool:
    if article_exists(db, article["id"]):
        return False
    db["articles"].insert_one(article)
    return True


def insert_articles(db: Database, articles: list[dict]) -> int:
    new_count = 0
    for article in articles:
        if insert_article(db, article):
            new_count += 1
    return new_count


def get_articles(db: Database) -> list[dict]:
    return list(db["articles"].find({}, {"_id": 0}))


def replace_clusters(db: Database, clusters: list[dict]) -> None:
    collection = db["clusters"]
    collection.delete_many({})

    if clusters:
        collection.insert_many(clusters)


def build_cluster(
    label: str,
    article_ids: list[str],
    start_time: str,
    end_time: str,
    cluster_id: int,
) -> dict:
    return {
        "cluster_id": cluster_id,
        "label": label,
        "article_ids": article_ids,
        "start_time": start_time,
        "end_time": end_time,
        "article_count": len(article_ids),
    }


def get_article_count(db: Database) -> int:
    return db["articles"].count_documents({})


def get_cluster_count(db: Database) -> int:
    return db["clusters"].count_documents({})