#!/bin/bash

trap exit SIGINT

out_dir="output"

mkdir -p "$out_dir"

i=0
batch_size=10

for in_file in pa193_dataset/dataset/*.txt; do
    out_file="$out_dir/$(basename "$in_file" .txt).json"
    echo "parsing \"$out_file\"..."
    python3 src/main.py "$in_file" --output_file "$out_file" &
    ((i = (i + 1) % batch_size)); ((i == 0)) && wait
done
