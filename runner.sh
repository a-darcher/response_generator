#!/bin/bash

DATASET_DIR="configs/uniform_dataset"

for config in "$DATASET_DIR"/*.yaml; do
   echo "$config"
   python3 src/response_stats/pipeline.py --config "$config"
done