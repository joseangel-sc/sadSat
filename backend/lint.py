#!/usr/bin/env python
"""
Simple script to run Ruff linter on the codebase
"""

import subprocess
import sys


def main():
    """Run Ruff linter on the codebase"""
    print("Running Ruff linter...")

    # Check code
    result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)

    if result.returncode != 0:
        print("Linting errors found:")
        print(result.stdout)
        return 1

    # Format code
    result = subprocess.run(["ruff", "format", "."], capture_output=True, text=True)

    if result.returncode != 0:
        print("Formatting errors:")
        print(result.stdout)
        return 1

    print("Linting successful!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
