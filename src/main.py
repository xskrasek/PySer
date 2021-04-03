#!/usr/bin/env python3

import parser

import argparse


def generate_json_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf8") as file:
        input = file.read()

    output = parser.generate_json(input)

    with open(output_path, "w", encoding="utf8") as file:
        file.write(output)


def parse_args():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("input_file", type=str)
    argument_parser.add_argument("--output_file", type=str, default="output.json")
    return argument_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_json_file(args.input_file, args.output_file)
