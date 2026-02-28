---
title: What is uv?
image: uv
tags:
- Python
---
## Description

uv is an extremely fast Python package and project manager, written in Rust.[^1]

## Installing uv [^2]

### Linux and macOS

Use curl to download the script and execute it with sh:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If your system doesn't have curl, you can use wget:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

Request a specific version by including it in the URL:

```bash
curl -LsSf https://astral.sh/uv/0.5.14/install.sh | sh
```

### Windows

Use irm to download the script and execute it with iex:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Changing the execution policy allows running a script from the internet.

### Alternative Method

Download the appropriate installer from the [releases page](https://github.com/astral-sh/uv/releases/latest) and run it.

[^1]: https://docs.astral.sh/uv/
[^2]: https://docs.astral.sh/uv/getting-started/installation/#installation-methods
