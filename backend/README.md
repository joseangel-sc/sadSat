# Backend Linting with Ruff

## Setup

1. Install dependencies including Ruff:
   ```
   pip install -r requirements.txt
   ```

2. The configuration is in `pyproject.toml` with the following rules:
   - Enforces absolute imports (no relative imports like `.scraper`)
   - Forces single-line imports (no grouped imports)
   - Sets line length to 100 characters

## Running the linter

You can run the linter in two ways:

### Option 1: Using the lint script

```
python lint.py
```

### Option 2: Using Ruff directly

To check your code:
```
ruff check .
```

To automatically fix issues:
```
ruff check --fix .
```

To format your code:
```
ruff format .
``` 