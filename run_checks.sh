#!/bin/bash

# Create checks directory if it doesn't exist
mkdir -p checks

# Generate log file with timestamp in checks folder
LOG_FILE="checks/checks_$(date +%Y%m%d_%H%M%S).log"

echo "Running code quality checks..." | tee "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running black formatter..." | tee -a "$LOG_FILE"
black src/ 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running isort..." | tee -a "$LOG_FILE"
isort src/ 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running flake8..." | tee -a "$LOG_FILE"
flake8 src/ --max-line-length=120 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running pylint..." | tee -a "$LOG_FILE"
pylint src/ 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running mypy..." | tee -a "$LOG_FILE"
mypy src/ 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Running interrogate..." | tee -a "$LOG_FILE"
interrogate --ignore-init-method --fail-under=100 . 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "======================================" | tee -a "$LOG_FILE"
echo "All checks completed. Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"