# PySer

A tool for parsing security certificates.

## Usage

`src/main.py` parses text files and outputs JSON files. It accepts options in the following format `[-h] [--output_folder OUTPUT_FOLDER] input_files [input_files ...]`. Option `-h` shows help, option `--output_folder` specifies the output folder and defaults to the current folder and `input_files [input_files ...]` specifies one or more input files.

## Bash scripts

`parse.sh` and `eval.sh` are meant to be run in the root directory of the project. A folder named `output` will be created and used to store the results of parsing.
