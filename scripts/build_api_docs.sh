#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DOCS_DIR="$ROOT_DIR/docs-api"
API_BUILD_DIR="$API_DOCS_DIR/_build/html"
DOCS_STATIC_API_DIR="$ROOT_DIR/docs-site/static/api-ref"

echo "Cleaning old API docs..."
rm -rf "$API_BUILD_DIR"
rm -rf "$DOCS_STATIC_API_DIR"

echo "Building Sphinx API docs..."
sphinx-build -b html "$API_DOCS_DIR" "$API_BUILD_DIR"

echo "Copying API docs into Docusaurus static/api-ref..."
mkdir -p "$DOCS_STATIC_API_DIR"
cp -R "$API_BUILD_DIR"/. "$DOCS_STATIC_API_DIR"/

echo "Done."