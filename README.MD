# News Pulse

A take-home assessment project that aggregates news from multiple RSS feeds, extracts full article text, and clusters articles by topic using keyword overlap.

---

## Part 1 — Scraper

### How the Scraper Works

The scraper is started with the repository-level `run.py` entrypoint. It coordinates the following pipeline:

1. **Initialize the database** — A SQLite connection is opened for `scraper/news_pulse.db`. The `articles` and `clusters` tables are created if they do not already exist.
2. **Fetch RSS feeds** — `scraper/fetch.py` reads the BBC News, NPR, and Guardian World feeds with `feedparser`. Each entry is normalized into a common article record containing a title, summary, link, publication date, source, and a 16-character SHA-256 ID derived from the link. Missing links are ignored, feed HTML is stripped from summaries, and malformed feed dates fall back to the current UTC time.
3. **Extract article text** — `scraper/extract.py` downloads each article page and uses Trafilatura to extract the main body text. If a page cannot be downloaded or parsed, the article is retained with an empty `full_text` value and a warning is logged.
4. **Save and deduplicate articles** — `scraper/db.py` checks each article ID before inserting it. Articles with a link already stored in the database are skipped, while new articles are saved with their metadata and extracted full text.
5. **Build topic clusters** — `scraper/cluster.py` combines each article's title and RSS summary, removes punctuation, stopwords, and common editorial words, and keeps words longer than two characters. Articles are assigned to the first existing cluster containing an article that shares at least four meaningful keywords; otherwise, a new cluster is created. Comparing against individual cluster members prevents an accumulated keyword union from pulling loosely related articles into an oversized cluster. The three most frequent keywords become the cluster label, and the earliest and latest publication dates define its time range.
6. **Persist results and report totals** — Each run stores the generated clusters and prints counts for fetched articles, newly inserted articles, skipped duplicates, created clusters, and totals currently in the database.

The scraper continues when an individual feed or article page fails, logging the problem and processing the remaining items. Article deduplication is persistent because it is based on the link hash in SQLite. Cluster records are currently inserted for every run, so rerunning the scraper prevents duplicate articles but can add another set of cluster rows.

### RSS Feeds Used

Three public RSS feeds are ingested:

| Source             | Feed URL                                |
| ------------------ | --------------------------------------- |
| BBC News           | `http://feeds.bbci.co.uk/news/rss.xml`  |
| NPR                | `https://feeds.npr.org/1001/rss.xml`    |
| The Guardian World | `https://www.theguardian.com/world/rss` |

### Clustering Approach

**Keyword-overlap grouping** was chosen over TF-IDF for several reasons:

- **Simplicity**: No external NLP libraries are needed — just `re` and the standard library.
- **Transparency**: Clusters are easy to interpret since they're built from plain shared words.
- **Adequacy for the scope**: With ~30–50 articles per run, a lightweight approach is sufficient to surface groupings without the complexity of vectorization or similarity matrices.

The algorithm works by extracting meaningful keywords from each article's title + summary (lowercased, punctuation stripped, stopwords removed), then grouping articles that share at least **4** common keywords with an existing cluster member. Generic reporting words such as `says`, `news`, and `year` are excluded because they do not identify a topic. The cluster label is based on the most frequent keywords across its members.

### Overlap Threshold Tuning

The default threshold is **4 shared keywords**. This favors precision, so a cluster represents articles with strong keyword overlap:

- **Threshold 1–2**: Produced large, noisy clusters because a small amount of shared vocabulary was enough to merge articles.
- **Threshold 3**: Offered a moderate balance but still grouped some broadly related stories.
- **Threshold 4**: Requires stronger topical similarity and keeps unrelated stories separate.

### Limitations

The clustering is **greedy and order-dependent**: articles are assigned to the first cluster that meets the overlap threshold, so the final groupings depend on the order articles are processed. This means two articles that should be in the same cluster could end up separate if they're processed in different batches or if no intermediate article bridges them. Additionally, the approach has no semantic understanding — "car" and "automobile" are treated as completely different words, and synonyms or paraphrases won't be matched.

### How to Run

```bash
python run.py
```

**No environment variables required.** The script will:

1. Fetch articles from the three RSS feeds
2. Extract full article text using trafilatura
3. Cluster articles by keyword overlap
4. Store everything in `scraper/news_pulse.db`
5. Print a summary to the console

**Expected output:**

```
--- Summary ---
Articles fetched:      45
New articles inserted: 45
Duplicates skipped:    0
Clusters created:      12
Total articles in DB:  45
Total clusters in DB:  12
```

On subsequent runs, duplicate articles (by URL hash) are automatically skipped, so the script is safely re-runnable.
