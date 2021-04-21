#!/usr/bin/env python3

import parser
import argparse
import json
import os
from typing import List
import sys


def generate_json_file(input_path: str, output_path: str):
    max_read = 64 * 1024 * 1024

    with open(input_path, "r", encoding="utf8") as file:
        input = file.read(max_read)
        if len(input) == max_read:
            raise MemoryError("File is too large")

    output = json.dumps(parser.parse(input), indent=4, ensure_ascii=False)

    with open(output_path, "w", encoding="utf8") as file:
        file.write(output)


def generate_multiple_json_files(input_files: List[str], output_folder: str):
    if not os.path.isdir(output_folder):
        print(f"No such directory: '{output_folder}'", file=sys.stderr)
        return

    for input_file in input_files:
        basename = os.path.splitext(input_file)[0]
        basename = os.path.basename(basename)
        output_file = output_folder + "/" + basename + ".json"

        try:
            generate_json_file(input_file, output_file)
        except Exception as e:
            print(f"Skipping file '{input_file}': {e}", file=sys.stderr)


def parse_args():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("input_files", type=str, nargs='+')
    # TODO: might be a good idea to remove some of those,
    # looks like a possible security hole?
    argument_parser.add_argument("--output_folder", type=str, default=".")
    return argument_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_multiple_json_files(args.input_files, args.output_folder)
