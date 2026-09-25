# News Pulse

News Pulse is a Python-based news aggregation and clustering project designed to pull stories from multiple RSS feeds, extract article text, and group related items by topic. The project is structured as a small end-to-end pipeline: scrape, extract, store, and cluster news content for later use in a backend or UI layer.

The repository is organized into three main areas:

- `scraper/` — the live ingestion and clustering pipeline
- `backend/` — server-side application code and API-layer work
- `frontend/` — client-side interface work for visualizing the collected stories

---

## What the project does

News Pulse continuously gathers articles from several public news sources, normalizes them into a common schema, and attempts to identify thematically related stories.

The workflow is:

1. Fetch RSS entries from multiple feeds
2. Normalize article metadata such as title, summary, published date, source, and link
3. Download each article page and extract the main text body
4. Deduplicate entries before saving them
5. Group related articles into topic clusters based on keyword overlap
6. Store the results in MongoDB for later access by the backend or frontend

---

## Current architecture

### Scraper

The scraper is the working core of the project. It uses:

- `feedparser` to read RSS feeds
- `trafilatura` to extract article text from webpages
- `pymongo` to store data in MongoDB
- `python-dotenv` to load configuration from environment variables

It processes feeds from sources such as:

- BBC News
- NPR
- The Guardian World

Each article gets a stable ID based on the article URL so duplicate entries can be skipped across runs.

### MongoDB storage

The project is configured to use MongoDB instead of a local SQLite file. The database layer expects the following environment settings in `scraper/.env`:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
DB_NAME=news_pulse
```

The `articles` and `clusters` collections are created with indexes to support fast deduplication and retrieval.

### Clustering logic

The clustering step uses keyword-overlap logic rather than ML models. It does the following:

- Lowercases and cleans article text
- Removes stopwords and common editorial noise
- Keeps meaningful keywords longer than two characters
- Compares article keywords against existing cluster members
- Creates a new cluster when the overlap is too weak
- Uses the most common keywords as the cluster label

This keeps the implementation lightweight, explainable, and easy to debug.

---

## Repository structure

```text
news pulse/
├── README.MD
├── run.py
├── scraper/
│   ├── __init__.py
│   ├── .env
│   ├── .env.example
│   ├── cluster.py
│   ├── db.py
│   ├── extract.py
│   ├── fetch.py
│   ├── requirements.txt
│   └── run.py
├── backend/
│   └── src/
├── frontend/
│   └── src/
├── plans/
├── part1.plan.md
└── .gitignore
```

---

## Setup

1. Create a virtual environment if needed.
2. Install scraper dependencies:

```bash
pip install -r scraper/requirements.txt
```

3. Create `scraper/.env` with your MongoDB connection string and database name.
4. Run the scraper:

```bash
python -m scraper.run
```

---

## Example output

```text
Starting News Pulse scraper
Fetched 88 total articles
Inserted 87 new articles (out of 88 fetched)
Clusters created: 82
Scraper run complete!
Total articles in DB: 87
Total clusters in DB: 82
```

---

## Notes

This project is a take-home assessment and prototype. The scraper is the most complete portion of the repository, while the backend and frontend are intended to build on the data produced by the ingestion and clustering pipeline.

The project is designed to be extendable: once articles and clusters are in MongoDB, the backend can expose them through APIs and the frontend can render them in a dashboard or news feed UI.
