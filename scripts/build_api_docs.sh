#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DOCS_DIR="$ROOT_DIR/docs-api"
API_BUILD_DIR="$API_DOCS_DIR/_build/html"
DOCS_STATIC_API_DIR="$ROOT_DIR/docs-site/static/api-ref"

echo "Cleaning old API docs..."
rm -rf "$API_BUILD_DIR"
rm -rf "$DOCS_STATIC_API_DIR"


# if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
#   source "$HOME/miniconda3/etc/profile.d/conda.sh"
# elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
#   source "$HOME/anaconda3/etc/profile.d/conda.sh"
# elif command -v conda >/dev/null 2>&1; then
#   eval "$(conda shell.bash hook)"
# else
#   echo "ERROR: conda not found. Is it installed?"
#   exit 1
# fi

#echo "Using conda env: dataset"
#conda run -n dataset sphinx-build -b html "$API_DOCS_DIR" "$API_BUILD_DIR"

echo "Copying API docs into Docusaurus static/api-ref..."
mkdir -p "$DOCS_STATIC_API_DIR"
cp -R "$API_BUILD_DIR"/. "$DOCS_STATIC_API_DIR"/

echo "Done."