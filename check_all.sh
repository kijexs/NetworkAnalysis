#!/bin/bash
echo "==> Black (check)"
black --check src tests experiments
echo "==> isort (check)"
isort --check-only src tests experiments
echo "==> flake8"
flake8 src tests experiments
echo "==> pytest"
pytest --cov=src --cov-report=term-missing tests/
