#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {".git", ".github", ".venv", "node_modules", "__pycache__"}
VALID_FILENAME_RE = re.compile(r"^[a-z0-9-]+\.md$")


@dataclass
class Issue:
    severity: str
    kind: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "kind": self.kind,
            "path": self.path,
            "message": self.message,
        }


def iter_markdown_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[Issue]]:
    text = path.read_text(encoding="utf-8")
    rel_path = str(path)
    issues: list[Issue] = []

    if not text.startswith("---\n"):
        issues.append(Issue("error", "missing_frontmatter", rel_path, "missing YAML frontmatter opening delimiter"))
        return {}, issues

    lines = text.splitlines()
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        issues.append(Issue("error", "unterminated_frontmatter", rel_path, "missing YAML frontmatter closing delimiter"))
        return {}, issues

    frontmatter: dict[str, str] = {}
    for raw_line in lines[1:end_index]:
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip("'\"")

    return frontmatter, issues


def build_route_key(path: Path, frontmatter: dict[str, str], repo_root: Path) -> str:
    explicit_permalink = frontmatter.get("permalink", "").strip().strip("/")
    if explicit_permalink:
        return explicit_permalink
    return path.relative_to(repo_root).stem


def validate(repo_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    route_map: dict[str, list[str]] = defaultdict(list)

    for path in iter_markdown_files(repo_root):
        rel_path = str(path.relative_to(repo_root))
        frontmatter, parse_issues = parse_frontmatter(path)
        for issue in parse_issues:
            issues.append(Issue(issue.severity, issue.kind, rel_path, issue.message))
        if parse_issues:
            continue

        if "title" not in frontmatter:
            issues.append(Issue("error", "missing_title", rel_path, "frontmatter is missing title"))
        if "tags" not in frontmatter:
            if "tag" in frontmatter or "tage" in frontmatter:
                issues.append(Issue("error", "invalid_tags_key", rel_path, "frontmatter must use tags:, not tag: or tage:"))
            else:
                issues.append(Issue("error", "missing_tags_key", rel_path, "frontmatter is missing tags"))

        if not VALID_FILENAME_RE.match(path.name):
            issues.append(Issue("warning", "legacy_filename", rel_path, "filename is not lowercase kebab-case"))

        route_key = build_route_key(path, frontmatter, repo_root)
        route_map[route_key].append(rel_path)

    for route_key, paths in sorted(route_map.items()):
        if len(paths) < 2:
            continue
        joined_paths = ", ".join(paths)
        for rel_path in paths:
            issues.append(
                Issue(
                    "error",
                    "duplicate_route",
                    rel_path,
                    f"effective permalink '{route_key}' conflicts with: {joined_paths}",
                )
            )

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate markdown content and permalink safety.")
    parser.add_argument("--repo-root", default=".", help="Path to the content repository root.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument(
        "--max-warnings",
        type=int,
        default=50,
        help="Maximum warning lines to print in text mode before summarizing the remainder.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    issues = validate(repo_root)
    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")

    if args.format == "json":
        payload = {
            "ok": error_count == 0,
            "summary": {
                "errors": error_count,
                "warnings": warning_count,
            },
            "issues": [issue.as_dict() for issue in issues],
        }
        print(json.dumps(payload, indent=2))
    else:
        shown_warnings = 0
        suppressed_warnings = 0
        for issue in issues:
            if issue.severity == "warning":
                if shown_warnings >= args.max_warnings:
                    suppressed_warnings += 1
                    continue
                shown_warnings += 1
            print(f"{issue.severity.upper()}: {issue.path}: {issue.message}")
        if suppressed_warnings:
            print(f"WARNING: {suppressed_warnings} additional warnings suppressed")
        print(f"Summary: {error_count} errors, {warning_count} warnings")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
