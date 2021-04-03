import parser

import argparse

def generate_json_files(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf8") as file:
        input = file.read()

    output = parser.generate_json(input)

    with open(output_path, "w", encoding="utf8") as file:
        file.write(output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--output_file", type=str, default="output.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_json_files(args.input_file, args.output_file)
