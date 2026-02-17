![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet?logo=astral&logoColor=white)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![mypy](https://img.shields.io/badge/type%20checker-mypy-blue?logo=python&logoColor=white)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ccasatejada/03f61ec73dc92d55950a8c386e8aff14/raw/tests-badge.json)
![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ccasatejada/03f61ec73dc92d55950a8c386e8aff14/raw/coverage-badge.json)
![CI](https://github.com/ccasatejada/lastfm-releases-tracker/actions/workflows/ci.yml/badge.svg)

## create a .env file with the following
```shell
DATABASE_HOST="localhost"
DATABASE_USER="dbuser"
DATABASE_PASSWORD="password"
DATABASE_SCHEMA="lfm_release_tracker"
```

### psql:
```sql
create database lfm_release_tracker;
create user lastfm_user with encrypted password 'password';
grant all privileges on database lfm_release_tracker to lastfm_user;
alter DATABASE lfm_release_tracker OWNER TO lastfm_user;
```

## reminder and aliases

### run application with textual (for debugging)
```
textual console [-v|-x]
textual run main.py --dev
```

### run pre-commit via uv
```
uv run pre-commit run --all-files
```

### only mypy
```
uv run mypy .
```

### run tests with coverage
```
uv run pytest
```
