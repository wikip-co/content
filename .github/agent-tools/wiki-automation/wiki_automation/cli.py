from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

SKIP_DIRS = {".git", ".github", ".venv", "node_modules", "__pycache__"}
DEFAULT_TAGS = ["Research"]

TOOL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
GMAIL_READER_DIR = REPO_ROOT / ".github" / "agent-tools" / "gmail-reader"
WEB_SCRAPER_DIR = REPO_ROOT / ".github" / "agent-tools" / "web-scraper"
IMAGE_UPLOAD_DIR = REPO_ROOT / ".github" / "agent-tools" / "image-upload"
DEFAULT_OUTPUT_DIR = TOOL_DIR / "out"


@dataclass
class ArticleRecord:
    path: str
    title: str
    stem: str
    tags: list[str]
    permalink: str | None

    @property
    def route_key(self) -> str:
        if self.permalink:
            return self.permalink.strip("/")
        return self.stem


def normalize(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def slugify(text: str) -> str:
    return re.sub(r"-{2,}", "-", normalize(text).replace(" ", "-")).strip("-")


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    lines = text.splitlines()
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}

    metadata: dict[str, Any] = {}
    current_key: str | None = None
    list_values: dict[str, list[str]] = {}

    for raw_line in lines[1:end_index]:
        line = raw_line.rstrip()
        if not line:
            continue
        if line.lstrip().startswith("-") and current_key:
            value = line.lstrip()[1:].strip()
            list_values.setdefault(current_key, []).append(value)
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        metadata[current_key] = value.strip().strip("'\"")

    for key, values in list_values.items():
        metadata[key] = values

    return metadata


def load_articles(repo_root: Path) -> list[ArticleRecord]:
    articles: list[ArticleRecord] = []
    for path in sorted(repo_root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        metadata = parse_frontmatter(path)
        articles.append(
            ArticleRecord(
                path=str(path.relative_to(repo_root)),
                title=str(metadata.get("title", path.stem)),
                stem=path.stem,
                tags=[tag for tag in metadata.get("tags", []) if tag],
                permalink=metadata.get("permalink") or None,
            )
        )
    return articles


def score_match(title: str, article: ArticleRecord) -> float:
    title_norm = normalize(title)
    article_title_norm = normalize(article.title)
    stem_norm = normalize(article.stem)
    path_norm = normalize(article.path)

    exact_bonus = 0
    if title_norm == article_title_norm:
        exact_bonus = 35
    elif title_norm == stem_norm:
        exact_bonus = 30

    title_ratio = SequenceMatcher(None, title_norm, article_title_norm).ratio()
    stem_ratio = SequenceMatcher(None, title_norm, stem_norm).ratio()
    path_ratio = SequenceMatcher(None, title_norm, path_norm).ratio()

    title_tokens = set(title_norm.split())
    article_tokens = set(article_title_norm.split()) | set(stem_norm.split())
    overlap = 0.0
    if title_tokens and article_tokens:
        overlap = len(title_tokens & article_tokens) / len(title_tokens)

    score = max(title_ratio, stem_ratio, path_ratio) * 70 + overlap * 30 + exact_bonus
    return min(score, 100.0)


def top_matches(
    articles: list[ArticleRecord],
    title: str,
    limit: int = 5,
    min_score: float = 30.0,
) -> list[dict[str, Any]]:
    matches = []
    for article in articles:
        score = score_match(title, article)
        if score < min_score:
            continue
        matches.append(
            {
                "path": article.path,
                "title": article.title,
                "tags": article.tags,
                "permalink": article.permalink,
                "route_key": article.route_key,
                "score": round(score, 2),
                "match_method": "score",
            }
        )
    matches.sort(key=lambda item: (-item["score"], item["path"].lower()))
    return matches[:limit]


def alert_name_matches_article(alert_name: str, article: ArticleRecord) -> bool:
    """Return True if any significant keyword from the alert name appears in the article path or title."""
    keywords = [kw for kw in re.split(r'[\s"\']+', alert_name.lower()) if len(kw) > 3]
    path_lower = article.path.lower()
    title_lower = article.title.lower()
    return any(kw in path_lower or kw in title_lower for kw in keywords)


def top_matches_extended(
    articles: list[ArticleRecord],
    title: str,
    alert_name: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Lower-threshold matching plus alert-name keyword matching for --match-existing."""
    seen_paths: set[str] = set()
    matches = []

    for article in articles:
        score = score_match(title, article)
        if score < 15:
            continue
        seen_paths.add(article.path)
        matches.append(
            {
                "path": article.path,
                "title": article.title,
                "tags": article.tags,
                "permalink": article.permalink,
                "route_key": article.route_key,
                "score": round(score, 2),
                "match_method": "score",
            }
        )

    if alert_name:
        for article in articles:
            if article.path in seen_paths:
                continue
            if alert_name_matches_article(alert_name, article):
                matches.append(
                    {
                        "path": article.path,
                        "title": article.title,
                        "tags": article.tags,
                        "permalink": article.permalink,
                        "route_key": article.route_key,
                        "score": 0.0,
                        "match_method": "alert_keyword",
                    }
                )

    matches.sort(key=lambda item: (-item["score"], item["path"].lower()))
    return matches[:limit]


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_tool_dir(path: Path, label: str) -> Path:
    if not path.is_dir():
        raise FileNotFoundError(f"{label} is missing at {path}")
    return path


def run_json_tool(tool_dir: Path, args: list[str]) -> dict[str, Any]:
    command = ["uv", "run", *args]
    result = subprocess.run(
        command,
        cwd=tool_dir,
        text=True,
        capture_output=True,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    payload_text = stdout or stderr
    if not payload_text:
        raise RuntimeError(f"Command produced no output: {' '.join(command)}")

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Command did not return JSON: {' '.join(command)}\nstdout={stdout}\nstderr={stderr}"
        ) from exc

    if result.returncode != 0 or not payload.get("ok", False):
        raise RuntimeError(payload.get("error", f"Command failed: {' '.join(command)}"))
    return payload["result"]


def article_stub(
    *,
    title: str,
    tags: list[str],
    image: str | None,
    permalink: str | None,
    abstract: str,
    footnote: str,
) -> str:
    frontmatter_lines = [
        "---",
        f"title: {title}",
    ]
    if permalink:
        frontmatter_lines.append(f"permalink: {permalink}")
    if image:
        frontmatter_lines.append(f"image: {image}")
    frontmatter_lines.append("tags:")
    for tag in tags:
        frontmatter_lines.append(f"- {tag}")
    frontmatter_lines.append("---")

    abstract_block = f"\n## Abstract\n\n{abstract}\n" if abstract else ""
    return "\n".join(frontmatter_lines) + (
        "\n\nBrief introduction.\n"
        "\n## Key Findings\n\n"
        "- Add the first validated finding here.[^1]\n"
        f"{abstract_block}"
        "\n## Notes\n\n"
        "- Review the scraped packet before publishing.\n\n"
        f"{footnote}\n"
    )


def unique_route_key(candidate_path: Path, articles: list[ArticleRecord]) -> str | None:
    route_key = candidate_path.stem
    existing = {article.route_key for article in articles}
    if route_key not in existing:
        return None
    parts = [slugify(part) for part in candidate_path.with_suffix("").parts if slugify(part)]
    return "/".join(parts)


def prepare_packet(args: argparse.Namespace) -> dict[str, Any]:
    ensure_tool_dir(WEB_SCRAPER_DIR, "web-scraper")
    output_dir = ensure_output_dir(Path(args.output_dir).expanduser().resolve())
    articles = load_articles(REPO_ROOT)

    source_slug = slugify(args.slug or Path(args.url).stem or "source")
    scrape_output_path = output_dir / f"{source_slug}-source.md"
    scrape = run_json_tool(
        WEB_SCRAPER_DIR,
        ["main.py", args.url, "--output", str(scrape_output_path)],
    )

    if args.match_existing:
        matches = top_matches_extended(
            articles,
            scrape["title"],
            alert_name=getattr(args, "alert_name", "") or "",
            limit=args.limit,
        )
    else:
        matches = top_matches(articles, scrape["title"], limit=args.limit)
    image_result = None
    image_public_id = args.image_public_id
    if args.image_file:
        ensure_tool_dir(IMAGE_UPLOAD_DIR, "image-upload")
        if not image_public_id:
            image_public_id = slugify(scrape["title"])
        upload_args = [
            "image-upload",
            args.image_file,
            "--public-id",
            image_public_id,
            "--validate-url",
        ]
        if args.image_folder:
            upload_args.extend(["--folder", args.image_folder])
        image_result = run_json_tool(IMAGE_UPLOAD_DIR, upload_args)
        image_public_id = image_result["public_id"]

    created_article_path = None
    suggested_article_path = None
    suggested_permalink = None
    selected_tags = args.tags or (
        matches[0]["tags"] if matches and matches[0]["score"] >= 75 and matches[0]["tags"] else DEFAULT_TAGS
    )

    if args.create_new or args.article_path:
        if args.article_path:
            relative_path = Path(args.article_path)
        elif args.category:
            relative_path = Path(args.category) / f"{slugify(scrape['title'])}.md"
        else:
            raise ValueError("--create-new requires --category or --article-path")

        if relative_path.is_absolute():
            raise ValueError("--article-path must be relative to the repo root")

        target_path = REPO_ROOT / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        suggested_article_path = str(relative_path)
        suggested_permalink = unique_route_key(relative_path, articles)
        if target_path.exists() and not args.overwrite:
            raise FileExistsError(f"Target article already exists: {relative_path}")

        stub = article_stub(
            title=args.title or scrape["title"],
            tags=selected_tags,
            image=image_public_id,
            permalink=suggested_permalink,
            abstract=scrape["abstract"],
            footnote=scrape["footnote_markdown"],
        )
        target_path.write_text(stub, encoding="utf-8")
        created_article_path = str(relative_path)

    packet = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "source_url": args.url,
        "scrape": scrape,
        "matches": matches,
        "selected_tags": selected_tags,
        "image_upload": image_result,
        "suggested_article_path": suggested_article_path,
        "suggested_permalink": suggested_permalink,
        "created_article_path": created_article_path,
    }

    packet_slug = slugify(scrape["title"]) or source_slug
    packet_path = output_dir / f"{packet_slug}-packet.json"
    packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    packet["packet_path"] = str(packet_path)

    # Mark the article as processed in the gmail-reader DB (non-fatal if unavailable)
    try:
        run_json_tool(GMAIL_READER_DIR, ["gmail-reader", "mark-processed", args.url])
    except Exception:
        pass

    return packet


def queue_articles(args: argparse.Namespace) -> dict[str, Any]:
    ensure_tool_dir(GMAIL_READER_DIR, "gmail-reader")
    output_dir = ensure_output_dir(Path(args.output_dir).expanduser().resolve())
    articles = load_articles(REPO_ROOT)

    search_args = [
        "gmail-reader",
        "search",
        "--gmail-query",
        args.gmail_query,
        "--days-back",
        str(args.days_back),
        "--max-messages",
        str(args.max_messages),
        "--max-results",
        str(args.max_results),
    ]
    if args.topic:
        search_args.extend(["--topic", args.topic])
    if args.include_review:
        search_args.append("--include-review")
    if args.save:
        search_args.append("--save")

    search_result = run_json_tool(GMAIL_READER_DIR, search_args)
    enriched_articles = []
    for item in search_result.get("articles", []):
        enriched_articles.append(
            {
                **item,
                "matches": top_matches(articles, item["title"], limit=args.limit),
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "search": search_result,
        "articles": enriched_articles,
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    queue_path = output_dir / f"queue-{timestamp}.json"
    queue_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["queue_path"] = str(queue_path)
    return payload


def match_title(args: argparse.Namespace) -> dict[str, Any]:
    articles = load_articles(REPO_ROOT)
    return {
        "title": args.title,
        "matches": top_matches(articles, args.title, limit=args.limit),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Agent orchestration helpers for the content repository."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    match_parser = subparsers.add_parser("match", help="Find likely existing article matches for a title.")
    match_parser.add_argument("title", help="Title or topic to match against the content repo.")
    match_parser.add_argument("--limit", type=int, default=5, help="Maximum matches to return.")

    queue_parser = subparsers.add_parser("queue", help="Build a cron-friendly candidate queue from Gmail Reader.")
    queue_parser.add_argument("--topic", help="Optional topic filter for gmail-reader search.")
    queue_parser.add_argument("--gmail-query", default="label:inbox newer_than:1d", help="Additional Gmail query terms.")
    queue_parser.add_argument("--days-back", type=int, default=1, help="Mailbox search window.")
    queue_parser.add_argument("--max-messages", type=int, default=25, help="Maximum messages to inspect.")
    queue_parser.add_argument("--max-results", type=int, default=10, help="Maximum article results to keep.")
    queue_parser.add_argument("--limit", type=int, default=5, help="Maximum content matches per result.")
    queue_parser.add_argument("--include-review", action="store_true", help="Include gmail-reader review items.")
    queue_parser.add_argument("--save", action="store_true", help="Persist parsed mail back into the gmail-reader database.")
    queue_parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for the generated queue packet.")

    prepare_parser = subparsers.add_parser("prepare", help="Scrape a URL, match it to the repo, and optionally create a new article stub.")
    prepare_parser.add_argument("url", help="URL to scrape.")
    prepare_parser.add_argument("--title", help="Optional title override for a newly created article.")
    prepare_parser.add_argument("--slug", help="Optional slug for packet file names.")
    prepare_parser.add_argument("--category", help="Relative category path for a new article.")
    prepare_parser.add_argument("--article-path", help="Explicit relative output path for a new article.")
    prepare_parser.add_argument("--create-new", action="store_true", help="Create a new article stub.")
    prepare_parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing target article.")
    prepare_parser.add_argument("--tag", dest="tags", action="append", default=[], help="Tag to place on a newly created article. Repeatable.")
    prepare_parser.add_argument("--image-file", help="Optional local image file to upload before creating a new article.")
    prepare_parser.add_argument("--image-public-id", help="Optional Cloudinary public ID for the article image.")
    prepare_parser.add_argument("--image-folder", help="Optional Cloudinary folder for uploaded images.")
    prepare_parser.add_argument("--limit", type=int, default=5, help="Maximum match candidates to return.")
    prepare_parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated scrape packets.")
    prepare_parser.add_argument(
        "--match-existing",
        action="store_true",
        help="Lower match threshold to 15 and also match by alert name keywords.",
    )
    prepare_parser.add_argument(
        "--alert-name",
        default="",
        help="Alert name for keyword matching when --match-existing is set.",
    )

    backlog_parser = subparsers.add_parser(
        "backlog",
        help="Query the gmail-reader DB for unprocessed candidate articles.",
    )
    backlog_parser.add_argument(
        "--status",
        choices=["selected", "review", "rejected", "all"],
        default="selected",
    )
    backlog_parser.add_argument("--min-score", type=int, default=0)
    backlog_parser.add_argument(
        "--source",
        help="Domain keyword filter (e.g. 'frontiersin', 'mdpi').",
    )
    backlog_parser.add_argument("--open-access", action="store_true")
    backlog_parser.add_argument("--include-processed", action="store_true")
    backlog_parser.add_argument("--limit", type=int, default=20)

    return parser


def backlog_query(args: argparse.Namespace) -> dict[str, Any]:
    ensure_tool_dir(GMAIL_READER_DIR, "gmail-reader")
    backlog_args = [
        "gmail-reader",
        "backlog",
        "--status", args.status,
        "--min-score", str(args.min_score),
        "--limit", str(args.limit),
    ]
    if args.source:
        backlog_args.extend(["--source", args.source])
    if args.open_access:
        backlog_args.append("--open-access")
    if args.include_processed:
        backlog_args.append("--include-processed")
    return run_json_tool(GMAIL_READER_DIR, backlog_args)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "match":
            result = match_title(args)
        elif args.command == "queue":
            result = queue_articles(args)
        elif args.command == "prepare":
            result = prepare_packet(args)
        elif args.command == "backlog":
            result = backlog_query(args)
        else:
            parser.error(f"Unsupported command: {args.command}")
            return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
