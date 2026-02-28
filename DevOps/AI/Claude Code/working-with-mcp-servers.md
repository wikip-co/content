---
title: Working with MCP Servers and Claude Code
image: bash
tags:
- Claude
- MCP
- Tools
- CLI Tools
---
## Description

Giving claude code access to the browser.

# Example location – anything outside ~/.config/BraveSoftware is fine
`mkdir -p ~/.local/share/claude-code/brave-persistent`

To start from your current cookies, copy once and never touch the source again:
- `cp -a ~/.config/BraveSoftware/Brave-Browser/Default/. ~/.local/share/claude-code/brave-persistent/`
  - (On most Linux distros that `~/.config/BraveSoftware/Brave-Browser` path is Brave’s default profile home.)

# Remove the current entry
`claude mcp remove playwright-brave`

# Re-add with --user-data-dir pointing at the new folder
```bash
claude mcp add-json playwright-brave \
'{
  "type": "stdio",
  "command": "npx",
  "args": [
    "@playwright/mcp@latest",
    "--browser", "chromium",
    "--executable-path", "/usr/bin/brave-browser",
    "--user-data-dir", "/home/anthony/.local/share/claude-code/brave-persistent"
  ]
}'
```
Test it out:
```bash
claude --allowedTools mcp__playwright-brave__browser_navigate -p  "can you open a browser using playwright-brave mcp and close any existing tabs"
```

## Sources
[^1] [^2] [^3] [^4]

[^1]: https://www.anthropic.com/engineering/claude-code-best-practices
[^2]: https://github.com/microsoft/playwright-mcp
[^3]: https://github.com/anthropics/claude-code/issues/626
[^4]: https://til.simonwillison.net/claude-code/playwright-mcp-claude-code
