---
title: Shared Content Project Guide
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

This project separates shared markdown content from the Hexo sites that render and publish it.

- `wikip-co/content` is the shared markdown repository.
- `wikip-co/wikip.co` is the sample Hexo site repository.
- `anthonyrussano/anthonyrussano.com` is a second site repository that receives the same content dispatch events.
- `wikip-co/public` receives the generated static output for `wikip.co`.

The key design choice is that content remains the single source of truth while each site keeps its own theme, Hexo configuration, deployment settings, and runtime integrations.

## Current Architecture

[Diagram bundle gist](https://gist.github.com/anthonyrussano/1fba3ca3d4781ffc5d7653a46cbf32be)

![Shared Content Project Architecture](https://gist.githubusercontent.com/anthonyrussano/1fba3ca3d4781ffc5d7653a46cbf32be/raw/cb734a78374035b29ff025615d767d4fa376944f/shared-content-architecture.svg)

The diagram source for this image is committed in `.github/project-docs/diagrams/specs/shared-content-architecture.yaml`.

## How Deploys Work

![Content Contribution And Deploy Flow](https://gist.githubusercontent.com/anthonyrussano/1fba3ca3d4781ffc5d7653a46cbf32be/raw/eca1823b8237e85607321c5347d943715cf2eaf8/contribution-and-deploy-flow.svg)

The deploy path is:

1. A contributor edits markdown in `wikip-co/content` and pushes to `main`.
2. `trigger-sites.yml` fires only for markdown changes.
3. That workflow sends `repository_dispatch` events to the site repositories and includes the exact `content_ref` and `content_sha`.
4. The site repo workflow calls the reusable `hexo-deploy.yml` workflow from the content repo.
5. The reusable workflow initializes `public` shallowly, initializes the content submodule with full history, resolves the content submodule to the dispatched SHA, restores markdown mtimes from Git history, builds Hexo, and publishes the generated output.

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
- `git submodule update --init --recursive` in site repos so `site/source/_posts` and `public` are present.

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

1. Make the corresponding workflow or theme changes in the site repo.
2. Keep reusable build logic in the content repo workflow when the logic is shared.
3. Keep site-specific behavior in the site repo.
4. When a workflow must reference a reusable workflow, pin it to an immutable content commit rather than a moving branch.

### Agent Tool Changes

1. Keep tool surfaces small and JSON-oriented.
2. Prefer additive improvements over brittle orchestration rewrites.
3. Document any local-only dependencies in the same change.
4. Verify the wrapper commands you changed, not just the underlying library code.

## Contribution Checklist

- New articles use explicit `image:` when a fallback image would be ambiguous.
- Dispatch workflows pass the exact content SHA through to site builds.
- Reusable workflow refs are pinned intentionally.
- Documentation and implementation change together.

## Where The Diagram Sources Live

The current architecture specs are committed under:

- `.github/project-docs/diagrams/specs/shared-content-architecture.yaml`
- `.github/project-docs/diagrams/specs/contribution-and-deploy-flow.yaml`
- `.github/project-docs/diagrams/specs/manual-agent-flow.yaml`

The rendered SVGs are published in the gist linked above so they can be referenced directly from documentation without depending on local build artifacts.
