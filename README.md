![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet?logo=astral&logoColor=white)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![mypy](https://img.shields.io/badge/type%20checker-mypy%20strict-blue?logo=python&logoColor=white)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

## create a .env file with the following
```shell
DATABASE_HOST="localhost"
DATABASE_USER="dbuser"
DATABASE_PASSWORD="password"
DATABASE_SCHEMA="lfm_release_tracker"
```

## reminder and aliases
  
### run application with textual (for debugging)
```
textual console [-v|-x]  
textual run main.py --dev
``` 

### run pre-commit via uv
``
uv run pre-commit run --all-files
``
