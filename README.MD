# News Pulse

News Pulse is a news aggregation and clustering project that pulls stories from multiple RSS feeds, extracts article text, groups related items by topic, and exposes the results through an API for a frontend timeline.

The repository is organized into three main areas:

- `scraper/` — the live ingestion and clustering pipeline
- `backend/` — Express and Mongoose API
- `frontend/` — React and Vite client application

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

Each article gets a stable ID based on its URL so duplicate articles are skipped across runs.

The pipeline loads all stored articles before clustering. Each run replaces the existing cluster snapshot instead of appending duplicate clusters, while preserving the article collection.

### Backend API

The backend uses Express and Mongoose to read the scraper's MongoDB collections. It exposes:

| Method | Endpoint                | Purpose                         |
| ------ | ----------------------- | ------------------------------- |
| `GET`  | `/health`               | Check API availability          |
| `GET`  | `/clusters`             | List stored clusters            |
| `GET`  | `/clusters/:id`         | Get a cluster and its articles  |
| `GET`  | `/timeline`             | Get timeline-ready cluster data |
| `POST` | `/ingest/trigger`       | Start a scraper job             |
| `GET`  | `/ingest/status/:jobId` | Check scraper job status        |

`POST /ingest/trigger` starts the Python pipeline asynchronously and returns a job ID with `202 Accepted`. Poll `/ingest/status/:jobId` until the status is `completed` or `failed`. Each job keeps the latest 4,000 characters of Python `stdout` and `stderr` for debugging. Job history is held in memory and is cleared when the backend restarts.

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

The backend and scraper must use the same `MONGODB_URI` and `DB_NAME`. The backend passes `DB_NAME` explicitly to Mongoose so it reads the same database as the Python process.

---

## Repository structure

```text
news pulse/
├── README.MD
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
│   ├── index.js
│   ├── package.json
│   └── src/
├── frontend/
│   ├── package.json
│   └── src/
├── plans/
├── part1.plan.md
└── .gitignore
```

---

## Setup

### 1. Configure MongoDB

Create `scraper/.env` and `backend/.env`. Use the same MongoDB connection in both files:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
DB_NAME=news_pulse
```

The backend also accepts `PORT` and `PYTHON_EXECUTABLE`. Never commit `.env` files.

### 2. Install scraper dependencies

From PowerShell:

```bash
cd scraper
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the scraper from the repository root so its package imports resolve correctly:

```powershell
scraper\.venv\Scripts\python.exe -m scraper.run
```

The scraper writes articles and clusters to MongoDB. Re-running it is safe for articles and replaces the cluster snapshot rather than duplicating cluster documents.

### 3. Install and run the backend

```bash
cd backend
pnpm install
pnpm dev
```

The API listens on `http://localhost:3000` by default.

### 4. Install the frontend

```bash
cd frontend
pnpm install
```

The frontend package includes React, Vite, and Recharts. The Vite app and API client still need to be added under `frontend/src/` before a development server can be started.

---

## Example output

```text
Starting News Pulse scraper
Fetched 88 total articles
Inserted 2 new articles (out of 88 fetched)
Clusters stored after this run: 86
Scraper run complete!
Total articles in DB: 88
Total clusters in DB: 86
```

## Notes

The scraper and backend are implemented. The frontend package and dependencies are initialized, while the React/Vite UI is still to be built under `frontend/src/`.
