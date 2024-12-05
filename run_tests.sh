#!/bin/bash

echo "Running pytest with coverage and verbose output..."
pytest -v --tb=short --disable-warnings "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Some tests failed. Exit code: $EXIT_CODE"
    exit $EXIT_CODE
else
    echo "All tests passed successfully!"
fi
