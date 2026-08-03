---
title: Wikip.co Content Project Guide
permalink: shared-content-project-guide/
image: git
tags:
- Git
- GitHub Actions
- CI/CD
- Hexo
- Documentation
- Contributing
---

## Overview

This project separates markdown content from the Hexo site that renders and publishes it.

- `wikip-co/content` is the shared markdown repository.
- `wikip-co/wikip.co` is the Hexo site repository.
- `wikip-co/public` receives the generated static output for `wikip.co`.

The key design choice is that content remains the single source of truth while the site keeps its theme, Hexo configuration, deployment settings, and runtime integrations. The repositories are standalone checkouts; none is linked as a Git submodule.

## Current Architecture

![Wikip.co Build-Fetch Architecture](https://raw.githubusercontent.com/wikip-co/Research/main/docs/diagrams/rendered/wikip-content-public-cicd.svg)

The diagram source is committed in `wikip-co/Research` under `docs/diagrams/specs/`.

## How Deploys Work

The deploy path is:

1. A contributor edits markdown in `wikip-co/content` and pushes to `main`.
2. `trigger-sites.yml` fires only for markdown changes.
3. That workflow sends a `repository_dispatch` event to `wikip.co` and includes the exact `content_ref` and `content_sha`.
4. The site workflow checks out that content SHA and the `public` repository into temporary build directories.
5. It copies content into a plain `_posts` tree, restores markdown mtimes from Git history, builds Hexo, and pushes generated output to `wikip-co/public`.

Two implementation details matter:

- The global Hexo permalink format stays unchanged.
- Duplicate route risks are handled with targeted `permalink:` overrides inside the content files that actually collide.

## Manual Agent Workflow

![Manual Agent Tooling Flow](https://gist.githubusercontent.com/anthonyrussano/1fba3ca3d4781ffc5d7653a46cbf32be/raw/ceef1bbbe5928b1d06dd8c54fe8d5a9c96329c1d/manual-agent-flow.svg)

The manual operator entrypoint is `agent-workflow` from the `research-tools` repo or container runtime.

- `agent-workflow queue` builds a fresh intake packet from recent Gmail/Scholar messages.
- `agent-workflow match "<topic>"` scores likely existing articles before you touch any markdown.
- `agent-workflow prepare "<url>" ...` scrapes a source, builds a packet, and can create a new stub article when appropriate.
The wrapper keeps the workflow explicit and manually triggered. That is intentional. It avoids hiding repo mutations behind an opaque scheduled prompt while still giving a single entrypoint for repeated operator tasks.

## Local Prerequisites

To work on the content and site repos locally:

- `uv` for the Python-based agent tools.
- `python3` for tool execution.
- `node` and `npm` for Hexo site builds.
- `rsync` for materializing fetched content and generated output without nested Git metadata.

With `content` and `wikip.co` checked out as siblings, run `./scripts/build-site` from the site repository.

Additional local-only dependencies still exist for the agent tooling:

- `gmail-reader` expects authenticated `gws` access and keeps its SQLite backlog under `/var/lib/content-agent/gmail-reader/` in the container runtime.
- `image-upload` expects Cloudinary credentials from exported env vars or a local `.env`.
- the optional backup helper defaults to a local NAS path.

## How To Contribute

### Content Changes

1. Edit or add markdown in `wikip-co/content`.
2. If the article title or filename collides with an existing route, add a targeted `permalink:` override instead of changing the global permalink format.
3. Commit and push to `main`.

### Site Or Workflow Changes

1. Make workflow, fetch, build, or theme changes in the site repo.
2. Keep the content repo limited to markdown and its rebuild dispatch.
3. Keep site-specific behavior in the site repo.
4. Preserve the exact content SHA in dispatch-triggered builds.

### Agent Tool Changes

1. Keep tool surfaces small and JSON-oriented.
2. Prefer additive improvements over brittle orchestration rewrites.
3. Document any local-only dependencies in the same change.
4. Verify the wrapper commands you changed, not just the underlying library code.

## Contribution Checklist

- New articles use explicit `image:` when a fallback image would be ambiguous.
- Dispatch workflows pass the exact content SHA through to site builds.
- Build inputs are fetched explicitly; no submodule initialization is required.
- Documentation and implementation change together.

## Where The Diagram Sources Live

The current architecture spec is committed in `wikip-co/Research` at `docs/diagrams/specs/wikip-content-public-cicd.yaml`; its rendered SVG lives under `docs/diagrams/rendered/`.
