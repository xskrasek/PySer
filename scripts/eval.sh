#!/bin/bash

trap exit SIGINT

out_dir="output"

scores=""
lines=""
exit_code=0

for ref_file in pa193_dataset/dataset/*.json; do
    out_file="$out_dir/$(basename "$ref_file")"
    echo "evaluating \"$out_file\"..."
    if out=$(python3 pa193_dataset/output_compare.py "$out_file" "$ref_file" -v)
    then
        score=$(echo "$out" | head -n 1)
        partial_scores=$(echo "$out" | tail -n 1)
        scores="$scores $(echo "$score" | head -n 1)"
        lines="$lines\n $score $partial_scores $(basename "$out_file")"
    else
        exit_code=1;
    fi
done

# results
echo ""
echo "sum tit ver toc rev bib name"
echo -e "$lines" | sort -nr

# total
sum=0
count=0

for score in $scores; do
    ((sum+=score))
    ((count++))
done

possible=$((count * 100))
echo "total: $sum/$possible"

exit $exit_code
