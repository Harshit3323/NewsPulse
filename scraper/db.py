import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

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


def insert_cluster(
    db: Database,
    label: str,
    article_ids: list[str],
    start_time: str,
    end_time: str,
) -> int:
    clusters = db["clusters"]
    last_cluster = clusters.find_one(sort=[("cluster_id", -1)])
    cluster_id = (last_cluster["cluster_id"] + 1) if last_cluster else 1

    clusters.insert_one({
        "cluster_id": cluster_id,
        "label": label,
        "article_ids": article_ids,
        "start_time": start_time,
        "end_time": end_time,
        "article_count": len(article_ids),
    })
    return cluster_id


def get_article_count(db: Database) -> int:
    return db["articles"].count_documents({})


def get_cluster_count(db: Database) -> int:
    return db["clusters"].count_documents({})