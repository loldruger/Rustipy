## Installation for development
```bash
# Install uv, ruff and ty
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Install dependencies
uv add --dev ruff
uv add --dev ty

# Create a virtual environment and activate it
uv venv
source .venv/bin/activate

# Activate the virtual environment
source .venv/bin/activate

uv sync
```

## Distribution
After development, increment the version at `[project]` section in `[pyproject.toml]`

```bash
# Only build
uv run python scripts/build.py

# Build before ruff, ty, pytest
uv run python scripts/build.py --check

# Print tag based on pyproject.toml
uv run python scripts/build.py --print-tag

# Build, check, create the version tag, and push it to trigger PyPI publishing
uv run python scripts/build.py --release

# Preview the release git commands without creating or pushing a tag
uv run python scripts/build.py --release --dry-run
```
