#!/usr/bin/env python3
"""
research_scrape.py
Scrapes a research article URL using Scrapling's StealthyFetcher (handles JS/bot
protection), cleans the HTML with BeautifulSoup, then converts to rich markdown
via markitdown — preserving headings, tables, lists, and all body content.

Usage:
    python main.py <URL> [output_file.md]
"""

import sys
import tempfile
import os
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from markitdown import MarkItDown
from scrapling.fetchers import StealthyFetcher

# ── HTML cleaning ──────────────────────────────────────────────────────────────

CONTENT_SELECTORS = [
    ".html-body",        # MDPI article body
    "article",
    ".article-content",
    ".article-body",
    '[role="main"]',
    "main",
    ".post-content",
    ".entry-content",
    "#content",
    ".main-content",
]

UNWANTED_SELECTORS = [
    "nav", "header", "footer", "script", "style",
    ".sidebar", ".comments", ".social-share", ".related-posts",
    ".advertisement", ".navigation", ".menu", ".widget",
    ".header", ".footer", ".author-bio", ".newsletter-signup",
    ".subscription-box", ".article-notes",  # MDPI citation boxes
    "[class*='cookie']", "[class*='banner']", "[class*='popup']",
    "[id*='cookie']", "[id*='banner']", "[id*='popup']",
    "figure > figcaption",  # keep figures but can strip captions if noisy
]


def clean_html(raw_html: str) -> str:
    """Extract main content and strip nav/footer/ads."""
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unwanted elements globally first
    for sel in UNWANTED_SELECTORS:
        for el in soup.select(sel):
            el.decompose()

    # Try to narrow to main content area
    main = None
    for sel in CONTENT_SELECTORS:
        main = soup.select_one(sel)
        if main:
            break

    return str(main) if main else str(soup)


def html_to_markdown(html: str) -> str:
    """Convert an HTML string to markdown via a temp file."""
    md = MarkItDown()
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                     encoding="utf-8", delete=False) as f:
        f.write(html)
        tmp = f.name
    try:
        result = md.convert(tmp)
        return result.text_content.strip()
    finally:
        os.unlink(tmp)


# ── Scraping ───────────────────────────────────────────────────────────────────

def scrape_article(url: str) -> dict:
    print(f"[*] Fetching: {url}")

    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        disable_resources=False,
    )

    if not page:
        raise RuntimeError("Failed to fetch — got empty response.")

    raw_html = page.html_content  # full page HTML string from scrapling

    # ── Metadata via reliable meta tags ───────────────────────────────────────
    title = (
        page.css('meta[name="citation_title"]::attr(content)').get()
        or page.css("h1::text").get()
        or page.css("title::text").get()
        or "Unknown Title"
    )

    author_tags = page.css('meta[name="citation_author"]::attr(content)').getall()
    if author_tags:
        authors = ", ".join(a.strip() for a in author_tags if a.strip())
    else:
        author_els = (
            page.css('[class*="author"] [class*="name"]::text').getall()
            or page.css('[class*="author"]::text').getall()
        )
        authors = ", ".join(a.strip() for a in author_els if a.strip()) or "Unknown Authors"

    doi = (
        page.css('meta[name="citation_doi"]::attr(content)').get()
        or page.css('[class*="doi"]::text').get()
        or ""
    )
    journal = (
        page.css('meta[name="citation_journal_title"]::attr(content)').get()
        or page.css('meta[name="citation_publisher"]::attr(content)').get()
        or ""
    )
    pub_date = (
        page.css('meta[name="citation_publication_date"]::attr(content)').get()
        or page.css('meta[name="citation_date"]::attr(content)').get()
        or datetime.now().strftime("%Y")
    )
    keywords_tags = page.css('meta[name="citation_keywords"]::attr(content)').getall()
    keywords = ", ".join(k.strip() for k in keywords_tags if k.strip())

    abstract = (
        page.css('meta[name="citation_abstract"]::attr(content)').get()
        or page.css('meta[name="description"]::attr(content)').get()
        or ""
    )
    # abstract meta tags sometimes have HTML entities / tags inside — clean them
    if abstract:
        abstract = BeautifulSoup(abstract, "html.parser").get_text(" ", strip=True)

    # ── Body: clean HTML → markitdown → rich markdown ─────────────────────────
    cleaned = clean_html(raw_html)
    body_md = html_to_markdown(cleaned)

    return {
        "url": url,
        "title": title.strip(),
        "authors": authors,
        "abstract": abstract,
        "body": body_md,
        "doi": doi.strip(),
        "journal": journal.strip(),
        "pub_date": pub_date.strip(),
        "keywords": keywords,
    }


# ── Markdown output ────────────────────────────────────────────────────────────

def build_markdown(data: dict) -> str:
    doi_line = f"DOI: {data['doi']}" if data["doi"] else f"URL: {data['url']}"
    journal_line = f"Journal: {data['journal']}" if data["journal"] else ""

    citation_parts = [
        data["authors"],
        f'"{data["title"]}"',
        journal_line,
        data["pub_date"],
        doi_line,
    ]
    citation = ". ".join(p for p in citation_parts if p)

    keywords_section = f"\n## Keywords\n{data['keywords']}" if data["keywords"] else ""
    abstract_section = f"\n## Abstract\n{data['abstract']}" if data["abstract"] else ""

    return f"""# {data['title']}

> Scraped: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> Source: {data['url']}

---

## Metadata
- **Authors:** {data['authors']}
- **Journal:** {data['journal'] or 'N/A'}
- **Published:** {data['pub_date']}
- **DOI:** {data['doi'] or 'N/A'}
{keywords_section}{abstract_section}

---

## Full Content

{data['body']}

---

## Citation

{citation}

---

## Copilot Integration Instructions

Use the content above to update the relevant article in this repository.

- Incorporate all findings from the **Abstract** and **Full Content** sections
- Every new sentence or bullet point added must include an inline reference: `[Author et al., {data['pub_date']}]`
- Append the citation below to the `## References` section of the target article
- Add any new relevant keywords to the `keywords` section of the target article
- Do not remove or modify any existing content, citations, or keywords

**Citation to append:**
> {citation}
"""


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <URL> [output.md]")
        sys.exit(1)

    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "article_extract.md"

    try:
        data = scrape_article(url)
        markdown = build_markdown(data)

        Path(output_path).write_text(markdown, encoding="utf-8")
        print(f"[✓] Saved to: {output_path}")
        print(f"[✓] Title: {data['title']}")
        print(f"[✓] Authors: {data['authors']}")
        print(f"[✓] Journal: {data['journal']}")
        print(f"[✓] DOI: {data['doi']}")
        print(f"[✓] Keywords: {data['keywords'][:80]}{'...' if len(data['keywords']) > 80 else ''}")
        print(f"[✓] Abstract: {len(data['abstract'])} chars")
        print(f"[✓] Body: {len(data['body'])} chars")

    except Exception as e:
        print(f"[✗] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
