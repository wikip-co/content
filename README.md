# Shared Content Repository

This repository contains the unified markdown content for both wikip.co and anthonyrussano.com.

## Architecture

- **wikip-co/content** (this repo): Contains all markdown blog posts
- **wikip-co/wikip.co**: Site repository with hexo config, uses content as submodule at `site/source/_posts`
- **anthonyrussano/anthonyrussano.com**: Site repository with hexo config, uses content as submodule at `site/source/_posts`

## Workflow

When markdown files are modified in this repository:
1. GitHub Actions workflow triggers (`trigger-sites.yml`)
2. Sends `repository_dispatch` events to both site repos
3. Both site repos rebuild with the latest content from this submodule

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
