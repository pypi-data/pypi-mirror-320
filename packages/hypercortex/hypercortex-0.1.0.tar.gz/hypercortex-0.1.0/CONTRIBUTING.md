# Contributing to Hypercortex

Thank you for your interest in contributing to Hypercortex! This document provides guidelines and instructions for development.

## Development Setup

1. Clone the repository and set up your development environment:
```bash
git clone this-repo-link cloned_repo_folder
cd cloned_repo_folder
```

2. Set up the Python environment using uv:
```bash
uv venv
uv sync
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
```

## Code Style

This project uses several tools to maintain code quality:
- black for code formatting
- flake8 for style guide enforcement
- isort for import sorting
- mypy for type checking
- ruff for fast linting

Configuration for these tools can be found in `pyproject.toml` and `.flake8`.

## Testing

Run tests using pytest:
```bash
uv run pytest
```

## Making Changes

1. Create a new branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure all tests pass
3. Commit your changes following [conventional commits](https://www.conventionalcommits.org/)
4. Push your changes and create a pull request

## Building and Publishing

To build the package:
```bash
uv run python -m build
```

To publish to TestPyPI:
```bash
uv run twine upload --repository testpypi dist/*
```

To publish to PyPI:
```bash
uv run twine upload dist/*
```

## Need Help?

If you have questions or need help, feel free to:
- Open an issue
- Reach out to the maintainers
