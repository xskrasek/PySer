#!/bin/bash

out_dir="output"

scores=""
lines=""

for ref_file in pa193_dataset/dataset/*.json; do
    out_file="$out_dir/$(basename "$ref_file")"
    echo "evaluating \"$out_file\"..."
    score=$(python3 pa193_dataset/output_compare.py "$out_file" "$ref_file")
    scores="$scores $score"
    lines="$lines\n$score $(basename "$out_file")"
done

# results
echo ""
echo -e "$lines" | sort -nr

# stats
sum=0
min=100
max=0

for score in $scores; do
    ((sum+=score))
    min=$((score < min ? score : min))
    max=$((score > max ? score : max))
done

echo "total: $sum/5000, min: $min, max: $max"
