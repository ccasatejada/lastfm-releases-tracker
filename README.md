![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet?logo=astral&logoColor=white)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![mypy](https://img.shields.io/badge/type%20checker-mypy-blue?logo=python&logoColor=white)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ccasatejada/03f61ec73dc92d55950a8c386e8aff14/raw/tests-badge.json)
![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ccasatejada/03f61ec73dc92d55950a8c386e8aff14/raw/coverage-badge.json)
![CI](https://github.com/ccasatejada/lastfm-releases-tracker/actions/workflows/ci.yml/badge.svg)

# Last.fm Releases Tracker

A terminal UI app that tracks music releases for artists you listen to on Last.fm.

It scrapes your Last.fm listening history, finds the artists you scrobble the most, fetches their discographies, and lets you browse everything from a clean TUI — releases sorted by date, cover art, per-user tracking.

## Features

- **Users** — manage multiple Last.fm accounts; each user has their own artist list and scrobble counts
- **Artists** — browse all tracked artists with release and user counts
- **Releases** — browse all releases across all artists, sorted by date; select one to see cover art, metadata, and per-user status
- **Logs** — real-time log output from scraping and fetching operations

## Setup

### Database (PostgreSQL)

```sql
CREATE DATABASE lfm_release_tracker;
CREATE USER lastfm_user WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE lfm_release_tracker TO lastfm_user;
ALTER DATABASE lfm_release_tracker OWNER TO lastfm_user;
```

Copy `.env.example` to `.env` and fill in your database credentials.

### Install & run

```bash
uv sync
uv run alembic upgrade head
uv run python main.py
```

---

## Dev commands

### Run with Textual dev console (for debugging)

```bash
textual console [-v|-x]
textual run main.py --dev
```

### Linting & type checking

```bash
uv run pre-commit run --all-files
uv run mypy .
```

### Tests with coverage

```bash
uv run pytest
```
