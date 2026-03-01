# Contributing

Contributions are welcome — bug fixes, new features, documentation improvements, and test coverage all help.

## Setting up

xanax requires Python 3.12+. All development dependencies are in the `dev` extra:

```bash
git clone https://github.com/violhex/xanax
cd xanax
uv sync --extra dev
```

## Running checks

Before opening a PR, run all three checks locally:

```bash
# Tests
uv run pytest

# Tests with coverage
uv run pytest --cov=xanax

# Lint
uv run ruff check xanax/

# Format
uv run ruff format xanax/

# Type check
uv run mypy xanax/
```

CI runs `ruff check`, `ruff format --check`, and `mypy` on every PR. All three must pass.

## What to work on

Not sure where to start? Look for issues labelled [`good first issue`](https://github.com/violhex/xanax/labels/good%20first%20issue).

If you want to add a new feature, open an issue first to discuss it. This avoids building something that doesn't fit the project's direction.

Bug fixes don't need prior discussion — just open a PR.

## Pull requests

Use the existing [PR template](.github/pull_request_template.md). The checklist is there for a reason:

- **Tests** — new behaviour should be covered; bug fixes should include a regression test
- **Changelog** — user-facing changes belong in `docs/changelog.md` under `Unreleased`
- **Types** — all public functions need type annotations; mypy strict mode is enforced

Keep PRs focused. A single fix or feature per PR is easier to review than a batch of unrelated changes.

## Commit messages

Use the conventional commits format:

```
feat: add iter_tags() to Xanax and AsyncXanax
fix: handle missing retry_after header in RateLimitError
docs: add downloading guide
chore: bump ruff to 0.4.0
```

The scope is optional but helpful for larger changes:

```
feat(async): add aiter_tags()
fix(pagination): correct seed propagation on page 1
```

## Code style

ruff handles formatting and linting. The configuration is in `pyproject.toml` — don't adjust it in your PR.

A few things ruff won't catch:

- Keep public APIs consistent between `Xanax` and `AsyncXanax`. Every sync method should have an async equivalent
- Prefer Pydantic models over raw dicts for any structured data
- Validate parameters locally before making any network request, the same way `SearchParams` raises `ValidationError` before the first HTTP call

## Docs

Documentation lives in `docs/` and is built with MkDocs Material. Install the docs extras:

```bash
uv sync --extra docs
uv run mkdocs serve
```

If you're adding a new public method or model, update the relevant guide page and docstring. Auto-generated API reference pages under `docs/api/` are sourced from docstrings, so keep those accurate.

## License

By contributing, you agree that your changes will be licensed under the same [BSD-3-Clause license](LICENSE) as the rest of the project.
