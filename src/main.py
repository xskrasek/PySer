#!/usr/bin/env python3

import parser
import argparse
import json
import os
from typing import List


def generate_json_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf8") as file:
        input = file.read()

    output = json.dumps(parser.parse(input), indent=4, ensure_ascii=False)

    with open(output_path, "w", encoding="utf8") as file:
        file.write(output)


def generate_multiple_json_files(input_files: List[str], output_folder: str):
    for input_file in input_files:
        basename = os.path.splitext(input_file)[0]
        basename = os.path.basename(basename)
        output_file = output_folder + "/" + basename + ".json"

        generate_json_file(input_file, output_file)


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
