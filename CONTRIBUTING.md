# Contributing to FullSpectrumProcessor

Thank you for your interest in contributing! This project uses several automated checks to ensure code quality, consistency, and compliance. Please read the following guidelines before submitting a pull request.

---

## Automated Checks and Workflows

This repository uses GitHub Actions workflows to automatically check code quality, formatting, documentation, licensing, and more. These workflows run on every pull request and on pushes to certain branches.

### Overview of Workflows

- **Formatting Check**: Ensures code is formatted with [Black](https://black.readthedocs.io/en/stable/) and imports are ordered with [isort](https://pycqa.github.io/isort/).
- **PEP 8 Compliance Check**: Uses [flake8](https://flake8.pycqa.org/) to check for PEP 8 compliance and common Python issues.
- **Static Code Analysis**: Runs [pylint](https://pylint.org/) for deeper static analysis and code quality checks.
- **Type Checking**: Uses [mypy](http://mypy-lang.org/) to check for type errors and enforce type annotations.
- **Documentation Coverage**: Uses [interrogate](https://interrogate.readthedocs.io/) to ensure all code is properly documented with docstrings.
- **Build and Deploy Documentation**: Builds API documentation using [pdoc](https://pdoc.dev/) and deploys it to GitHub Pages.
- **License and Open Source Compliance Check**: Uses [pip-licenses](https://github.com/raimon49/pip-licenses) to ensure all dependencies have acceptable licenses.
- **Publish to GHCR**: Builds and publishes a Docker image to GitHub Container Registry (GHCR) on pushes to `main`.

---

## Running Checks Locally

Before submitting a pull request, please run the following checks locally to catch issues early:

### 1. Formatting

```sh
pip install black isort
black src/
isort src/
```

### 2. PEP 8 Compliance

```sh
pip install flake8
flake8 src/ --max-line-length=120
```

### 3. Static Analysis

```sh
pip install pylint
pylint src/
```

### 4. Type Checking

```sh
pip install mypy
mypy src/
```

### 5. Documentation Coverage

```sh
pip install interrogate
interrogate --ignore-init-method --fail-under=100 .
```

### 6. Build Documentation

```sh
pip install pdoc
pdoc --html --output-dir docs FullSpectrumProcessor
```

### 7. License Compliance

```sh
pip install pip-licenses
pip-licenses --from=mixed --fail-on=restricted
```

---

## Purpose of Each Workflow

- **Formatting Check**: Prevents unformatted code and unordered imports from being merged.
- **PEP 8 Compliance Check**: Ensures code follows Python style guidelines.
- **Static Code Analysis**: Detects code smells, bugs, and anti-patterns.
- **Type Checking**: Catches type errors and enforces type safety.
- **Documentation Coverage**: Ensures all public code is documented.
- **Build and Deploy Documentation**: Keeps API documentation up-to-date and available online.
- **License and Open Source Compliance Check**: Ensures all dependencies are properly licensed.
- **Publish to GHCR**: Provides up-to-date Docker images for deployment and testing.

---

## Submitting a Pull Request

1. Fork the repository and create your branch from `main`.
2. Make your changes.
3. Run all checks locally (see above).
4. Commit and push your changes.
5. Open a pull request and ensure all GitHub Actions checks pass.

If you have any questions, feel free to open an issue or ask in your pull request!

---
