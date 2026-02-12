#!/bin/bash

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <DATASET_DIR>"
  exit 1
fi

DATASET_DIR="$1"

# Optional: check if directory exists
if [ ! -d "$DATASET_DIR" ]; then
  echo "Error: Directory '$DATASET_DIR' does not exist."
  exit 1
fi

for config in "$DATASET_DIR"/*.yaml; do
   echo "$config"
   python3 src/response_stats/pipeline.py --config "$config"
done
