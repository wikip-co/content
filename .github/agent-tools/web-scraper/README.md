# Web Scraping Tool

This tool scrapes a URL and converts the article content to markdown for downstream repository updates.

## Location

`.github/agent-tools/web-scraper`

## Run

Using `uv` (preferred):

```bash
cd .github/agent-tools/web-scraper
uv run main.py "<URL>" "<output_file.md>"
```

Using `pip` + `python`:

```bash
cd .github/agent-tools/web-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py "<URL>" "<output_file.md>"
```

## Example

```bash
cd .github/agent-tools/web-scraper
uv run main.py "https://example.org/article" "../../Current Events/Research/article-review.md"
```

## Notes

- The script expects one required argument: URL.
- The second argument is optional output path.
- If no output path is provided, it defaults to `article_extract.md`.
