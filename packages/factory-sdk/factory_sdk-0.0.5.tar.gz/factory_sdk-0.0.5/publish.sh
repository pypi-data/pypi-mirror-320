#!/bin/bash

export TWINE_USERNAME="__token__"
export TWIN_PASSWORD="pypi-AgEIcHlwaS5vcmcCJDEzYjVhZjY5LWMwNjEtNDk4OC05MTMxLTdlNDkzZTI3ZjhjOAACKlszLCI0MGMxNmQ0NC0xZTk1LTRkNDQtODE1ZS1jNmRmMDM1MWM3NGUiXQAABiDEXYhBWp6WEH47tgCVNSjCgNezzz11JONro4CoiR3mEA"

# Exit immediately if a command exits with a non-zero status
set -e

echo "Cleaning previous builds..."
rm -rf dist

echo "Building the package..."
python setup.py sdist bdist_wheel


echo "Cleaning up generated .c files and build artifacts..."

# Remove all .c files
find . -name "*.c" -type f -delete


echo "Cleanup complete!"

echo "Uploading the package to PyPI..."
twine upload dist/*

echo "Package successfully uploaded to PyPI!"
