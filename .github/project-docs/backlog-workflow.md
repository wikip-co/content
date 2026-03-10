# Backlog-to-Content Workflow

The gmail-reader tool continuously ingests Google Scholar alert emails and scores each article as `selected`, `review`, or `rejected`. This document describes how to move articles from the **selected backlog** in SQLite into actual repo content using the agent-workflow tools.

---

## Prerequisites

Ensure the following tools are set up:

```bash
cd .github/agent-tools/gmail-reader && uv sync
cd .github/agent-tools/wiki-automation && uv sync
cd .github/agent-tools/web-scraper && uv sync   # required by prepare
```

Verify the backlog has candidates:

```bash
./agent-workflow backlog --status selected --limit 5
```

---

## Step 1 — Query the Backlog

Use the `backlog` command to surface unprocessed candidate articles from the SQLite DB. Articles with `processed_at IS NULL` are returned by default.

```bash
# Top 20 selected articles, any source
./agent-workflow backlog

# High-score open-access articles from Frontiers
./agent-workflow backlog --status selected --min-score 18 --source frontiersin --limit 20

# Any open-access source, score >= 15
./agent-workflow backlog --open-access --min-score 15 --limit 50

# Include articles already processed (audit mode)
./agent-workflow backlog --include-processed --limit 20
```

**Key filters:**

| Flag | Description |
|---|---|
| `--status` | `selected` (default), `review`, `rejected`, or `all` |
| `--min-score` | Integer threshold — scores in the backlog typically range from 8–22 |
| `--source` | Domain keyword: `frontiersin`, `mdpi`, `pmc`, `pubmed`, `springer`, etc. |
| `--open-access` | Only articles on recognized open-access domains |
| `--include-processed` | Include rows where `processed_at IS NOT NULL` |
| `--limit` | Max rows returned (default: 20) |

The output is JSON with an `articles` array. Each item includes `title`, `article_url`, `score`, `alert_name`, `is_open_access`, and `processed_at`.

---

## Step 2 — Choose a URL

From the backlog results, select an article URL based on:

- **Score** — prefer ≥ 18 for `selected` items
- **Open-access** — `is_open_access: 1` means the full text is freely available; the web-scraper will get richer content
- **Alert category** — `alert_name` indicates the topic (e.g. `"astragalus"`, `"quercetin"`, `"Green Tea"`)
- **Relevance** — check whether the existing repo already covers the topic well or if new content would add value
- **Study type** — systematic reviews and meta-analyses in the title/snippet are highest value

**Recognized open-access domains** (set at import time via `is_open_access`):
- `frontiersin.org`
- `mdpi.com`
- `pmc.ncbi.nlm.nih.gov`
- `pubmed.ncbi.nlm.nih.gov`

---

## Step 3 — Prepare the Article

The `prepare` command scrapes the URL, matches it against existing repo articles, optionally creates a new stub, and marks the article as processed in the DB.

**Basic scrape (no new file):**

```bash
./agent-workflow prepare "https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2026.1799944/full"
```

**Create a new article stub:**

```bash
./agent-workflow prepare "https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2026.1799944/full" \
  --category "Natural Healing/Botanicals" \
  --create-new \
  --tag "Wound Healing" \
  --tag "Anticancer"
```

**Use `--match-existing` to find the right existing article** (lowers match threshold from 30 → 15, and also searches by alert name keywords):

```bash
./agent-workflow prepare "https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2026.1799944/full" \
  --match-existing \
  --alert-name "astragalus"
```

**Full example — new article for infant nutrition topic:**

```bash
./agent-workflow prepare "https://example.org/infant-gut-microbiota" \
  --category "Child Development/Infant" \
  --create-new \
  --match-existing \
  --alert-name "infant nutrition" \
  --tag Nutrition \
  --tag "Gut Health"
```

After a successful `prepare`, the article's `processed_at` timestamp is set automatically in the DB. It will no longer appear in future `backlog` queries (unless `--include-processed` is passed).

---

## Step 4 — Review the Packet

The `prepare` command writes a JSON packet to `.github/agent-tools/wiki-automation/out/`. Check:

- `scrape.title` — confirm it scraped the right article
- `scrape.abstract` — the key content for writing findings
- `scrape.footnote_markdown` — pre-formatted citation to paste into the article
- `matches` — existing repo articles that matched; check `match_method` (`score` vs `alert_keyword`)
- `created_article_path` — path of the new stub file, if `--create-new` was used

Run the validator after any file changes:

```bash
./agent-workflow validate
```

---

## Step 5 — Update or Create Content

### Adding findings to an existing article

When `matches` contains high-scoring hits, add the research findings as new bullet points and a footnote to the existing article:

1. Read `scrape.abstract` to extract key findings
2. Add a new heading or bullet points under the appropriate `## Healing Properties` or `## Disease / Symptom Treatment` section
3. Append `scrape.footnote_markdown` as a new `[^N]` footnote at the end of the file
4. Add relevant tags to the frontmatter if needed

### Publishing a new stub

When `--create-new` was used, the stub at `created_article_path` is ready to edit:

1. Replace "Brief introduction." with a description of the topic
2. Fill in "Key Findings" from `scrape.abstract`
3. Expand the `## Abstract` section or remove it if redundant
4. Remove the "Review the scraped packet before publishing." note when done

---

## Common Filter Combinations

```bash
# Best open-access articles for today's session
./agent-workflow backlog --open-access --min-score 18 --limit 20

# Target a specific alert topic
./agent-workflow backlog --status selected --min-score 15 --limit 50 | \
  python3 -c "import sys,json; [print(a['score'], a['alert_name'], a['article_url']) for a in json.load(sys.stdin)['result']['articles'] if 'quercetin' in a['alert_name'].lower()]"

# Audit what's been processed
./agent-workflow backlog --include-processed --status selected | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(a['processed_at'], a['title'][:60]) for a in d['result']['articles'] if a['processed_at']]"

# Frontiersin only, any score
./agent-workflow backlog --source frontiersin --limit 30
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Backlog is empty | Run `gmail-reader sync` to pull new Scholar alert emails into the DB |
| `is_open_access` is always 0 | Run the backfill SQL: `UPDATE articles SET is_open_access=1 WHERE article_url LIKE '%frontiersin.org%' OR ...` |
| `processed_at` not being set | Confirm `gmail-reader mark-processed` is registered (run `uv run gmail-reader --help`) |
| Score too low for match | Add `--match-existing` and `--alert-name <topic>` to `prepare` |
| Scrape returns no abstract | The page may be paywalled; prefer `is_open_access=1` articles or use the `pdf_url` if available |
| New stub has wrong category | Delete the stub and re-run `prepare` with the correct `--category` path |
