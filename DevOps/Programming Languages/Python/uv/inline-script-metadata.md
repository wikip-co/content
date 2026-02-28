---
title: Managing Python Scripts with uv Inline Metadata
image: python
tags:
- Python
- Package Management
- DevTools
---
## Description

Managing Python script dependencies and version requirements has traditionally been challenging. The `uv` tool, combined with Python's new inline script metadata standard, offers a modern solution to this problem.

Python recently added a standard format for inline script metadata. It allows for selecting Python versions and defining dependencies in a section at the top of the script declaring the dependencies using TOML.

## What is Inline Script Metadata?

Python's inline script metadata format provides a standardized way to specify Python versions and dependencies directly within your scripts. When combined with `uv`, this creates a powerful workflow for managing script environments.

## Key Features
- Declare dependencies inline using TOML format
- Specify Python version requirements
- Automatic environment creation
- Isolated from project dependencies

## Prerequisites

- uv installed ( check out [this article](https://wikip.co/what-is-uv/) for more information)
- Basic familiarity with Python packaging

## Usage[^1]

Use `uv init --script` to initialize scripts with the inline metadata.

```bash
uv init --script example.py --python 3.12
```

### Declaring script dependencies

The inline metadata format allows the dependencies for a script to be declared in the script itself.

uv supports adding and updating inline script metadata for you.

Use `uv add --script` to declare the dependencies for the script.

```bash
uv add --script example.py 'requests<3' 'rich'
```

This will add a script section at the top of the script declaring the dependencies using TOML:

`example.py`
```python
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

uv will automatically create an environment with the dependencies necessary to run the script.

### Running the script

```bash
uv run example.py
```

When using inline script metadata, even if uv run is used in a project, the project's dependencies will be ignored.

uv also respects Python version requirements:

`example.py`
```python
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# Use some syntax added in Python 3.12
type Point = tuple[float, float]
print(Point)
```

The dependencies field must be provided even if empty.

- uv run will search for and use the required Python version.
- The Python version will download if it is not installed.

## Additional Resources
- [uv Documentation](https://docs.astral.sh/uv/)
- [PEP 723 - Inline Script Metadata](https://peps.python.org/pep-0723/)

[^1]: https://docs.astral.sh/uv/guides/scripts/#creating-a-python-script
