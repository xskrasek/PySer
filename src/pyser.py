#!/usr/bin/env python3

import parser
import pretty_printer
from common import parsed_fields_long, parsed_fields_short
import argparse
import itertools
import json
import os
import sys
from typing import List


def generate_json_file(sequence_number: int, input_path: str,
                       output_path: str, pretty_printed_fields: List[str]):
    with open(input_path, "r", encoding="utf8") as file:
        input = file.read()

    result = parser.parse(input)
    output = json.dumps(result, indent=4, ensure_ascii=False)
    
    if len(pretty_printed_fields) != 0:
        if sequence_number != 1:
            print(end="\n" * 2)
        print(f"{sequence_number}.", os.path.splitext(os.path.basename(input_path))[0])

    pretty_printer.pretty_print(result, pretty_printed_fields)

    with open(output_path, "w", encoding="utf8") as file:
        file.write(output)


def generate_multiple_json_files(input_files: List[str], output_folder: str,
                                 pretty_printed_fields: List[str]):
    for i, input_file in enumerate(input_files, start=1):
        basename = os.path.splitext(input_file)[0]
        basename = os.path.basename(basename)
        output_file = output_folder + "/" + basename + ".json"

        try:
            generate_json_file(i, input_file, output_file, pretty_printed_fields)
        except Exception as e:
            print(f"Skipping file '{input_file}': {e}", file=sys.stderr)


def parsed_fields(string: str) -> List[str]:
    if len(string) == 0:
        return []

    fields = string.split(",")
    fields = list(itertools.chain.from_iterable(
        parsed_fields_long if f == "all" else [f] for f in fields))
    
    for i in range(len(fields)):
        try:
            fields[i] = \
                parsed_fields_long[parsed_fields_short.index(fields[i])]
        except ValueError:
            pass
    
    if any(field not in parsed_fields_long for field in fields):
        raise argparse.ArgumentTypeError(
            f"'{string}' is not a valid fields option")

    fields = list(dict.fromkeys(fields))
    return fields


def parse_args():
    argument_parser = argparse.ArgumentParser(
        description="PySer - A regular expression based parser for security "
                    "certificates.")

    argument_parser.add_argument(
        "input_files",
        help="A list of input files in plaintext format.",
        type=str, nargs='+')
    # TODO: might be a good idea to remove some of those,
    # looks like a possible security hole?
    argument_parser.add_argument(
        "-o", "--output_folder",
        help="Path to an existing outupt folder, into which "
             "the correspondingly named list of JSON files will be written.",
        type=str, default=".")
    argument_parser.add_argument(
        "-p", "--pretty_print",
        help="A comma-separated list of the fields (without whitespace) "
             "to pretty-print after parsing each file. Allowed values are: " +
             ", ".join(parsed_fields_long) +
             " or their corresponding short form: " +
             ", ".join(parsed_fields_short) +
             ". The fields are printed in the specified order, "
             "without duplication.",
        metavar="FIELD_LIST",
        type=parsed_fields, default="")

    return argument_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_multiple_json_files(args.input_files, args.output_folder, args.pretty_print)
