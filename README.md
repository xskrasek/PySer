# PySer

A tool for parsing security certificates.

## Usage

`src/main.py` parses a text file and outputs a JSON file. It accepts options in the following format `[-h] [--output_file OUTPUT_FILE] input_file`. Option `-h` show help, option `--output_file` specifies the output file and defaults to `output.json` and `input_file` specifies the input file.

## Bash scripts

`parse.sh` and `eval.sh` are meant to be run in the root directory of the project. A folder named `output` will be created and used to store the results of parsing.
