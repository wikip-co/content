# Details

This repository contains the markdown articles for use in a hexo.js site.  This repo is a submodule in multiple other repos that contain hexo.js sites.

## Architecture

- **wikip-co/content** (this repo): Contains all markdown blog posts
- **wikip-co/wikip.co**: Site repository with hexo config, uses content as submodule at `site/source/_posts`
- **anthonyrussano/anthonyrussano.com**: Site repository with hexo config, uses content as submodule at `site/source/_posts`

## Workflow

When markdown files are modified in this repository:
1. GitHub Actions workflow triggers (`trigger-sites.yml`)
2. Sends `repository_dispatch` events to both site repos with the exact content commit SHA
3. Both site repos rebuild against that specific content revision

## Making Changes

To add or edit blog posts:
1. Clone this repository
2. Make changes to markdown files
3. Commit and push to main branch
4. Both sites will automatically rebuild with your changes

## Setup Notes

- Total files: 3,198 markdown posts
- Content merged from both site repos (wikip.co had 3,188, anthonyrussano.com had 3,195)
- Conflicts resolved: 2 files (kept best version of each)
- New content included from both repos

## Agent Tools

- `image-upload`: Cloudinary upload/search/download CLI for agents
- `web-scraper`: Article scraper that returns JSON plus a repo-compatible footnote
- `gmail-reader`: Google Scholar alert ingestion CLI backed by Gmail and SQLite
- `wiki-automation`: Queue builder and scrape-to-article orchestration helper

## Manual Launcher

- `./agent-workflow queue`: Build a fresh intake packet on demand
- `./agent-workflow match "<topic>"`: Find likely existing articles
- `./agent-workflow prepare "<url>" ...`: Scrape a URL and optionally create a stub article
- `./agent-workflow validate`: Run the content validator

## Validation

- `.github/scripts/validate_content.py`: Checks frontmatter, missing `tags:`, and duplicate effective permalinks by default
- `--warn-empty-tags`: Opt-in warning mode for legacy files whose `tags:` field exists but is still empty
- `--warn-legacy-filenames`: Opt-in warning mode for older non-kebab-case filenames that are still valid in the repo today
