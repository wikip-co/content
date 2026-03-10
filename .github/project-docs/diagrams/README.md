# Project Diagrams

These specs describe the current shared-content architecture, the deploy flow,
and the manual agent-tooling workflow for the content + Hexo site setup.

Generate the rendered diagrams from `/home/anthony/Workspace/diagram-generator`
with commands like:

```bash
cd /home/anthony/Workspace/diagram-generator
uv run diagram-gen spec \
  --spec /home/anthony/Workspace/content/.github/project-docs/diagrams/specs/shared-content-architecture.yaml \
  --output /home/anthony/Workspace/content/.github/project-docs/diagrams/rendered/shared-content-architecture \
  --format svg
```
