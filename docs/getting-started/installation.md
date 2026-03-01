# Installation

xanax requires **Python 3.12 or later** and has two runtime dependencies: [httpx](https://www.python-httpx.org/) and [pydantic](https://docs.pydantic.dev/).

## pip

```bash
pip install xanax
```

## uv

```bash
uv add xanax
```

## From source

```bash
git clone https://github.com/violhex/xanax
cd xanax
uv sync --extra dev
```

The `--extra dev` flag pulls in pytest, ruff, mypy, and pytest-asyncio for development work.

## Verifying the install

```python
import xanax
print(xanax.__version__)
```

## Python version

xanax uses `str | None` union syntax, `StrEnum`, and other features that require Python 3.12+. Older versions are not supported.
