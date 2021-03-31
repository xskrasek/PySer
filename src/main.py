import json
import re
from typing import Dict, List
import argparse

    
def find_title_dirty(input: str) -> str:
    input = input[:1000] # Arbitrary limit, title after 1000 characters would be weird.

    # For documents starting with 4 numbers only.
    iter = re.search(r"for\s\s+(.*?)\s\s+from", input.replace("\n", " "), re.MULTILINE)
    if iter:
        return iter.group(1)

    # e.g. NSCIB-CC-217812-CR2
    iter = re.search(r"Version [0-9]+-[0-9]+\s*(.*)", input, re.MULTILINE)
    if iter:
        return iter.group(1)

    # e.g. 1110V3b_pdf
    iter = re.search(r"\n\n([^\n].+?\n)\n\n", input, re.MULTILINE | re.DOTALL)
    if iter:
        return iter.group(1)

    # Last resort.
    iter = re.search(r"([^\n]+\n)*", input, re.MULTILINE)
    return iter.group(0)


def find_title(input: str) -> str:
    title = find_title_dirty(input)
    title = " ".join(title.split())
    return title


def find_eal(input: str) -> List[str]:
    found = re.findall(r"EAL ?[0-9]\+?", input)

    return list(set(found))


def find_sha(input: str) -> List[str]:
    input = input.replace(" ", "")
    found = re.findall(r"SHA[- ]?[0-9]+", input)

    return list(set(found))


def find_des(input: str) -> List[str]:
    found = re.findall(r"3des", input, re.IGNORECASE)
    found += re.findall(r"triple-des", input, re.IGNORECASE)
    found += re.findall(r"tdes", input, re.IGNORECASE)

    return list(set(found))


def find_rsa(input: str) -> List[str]:
    found = re.findall(r"RSA[- ]?[0-9]+", input)

    return list(set(found))


def find_ecc(input: str) -> List[str]:
    found = re.findall(r"ECC", input)
    found += re.findall(r"ECC ?[0-9]+", input)
    for i in range(len(found)):
        found[i] = found[i].upper()

    return list(set(found))


def find_versions(input: str) -> Dict[str, List[str]]:
    versions = {}
    for i in [("eal", find_eal),
              ("sha", find_sha),
              ("des", find_des),
              ("rsa", find_rsa),
              ("ecc", find_ecc)]:
        result = i[1](input)
        if result:
            versions[i[0]] = result
    return versions


def find_bibliography(input: str) -> Dict[str, str]:
    bib_references_found = set(re.findall(r"\[[0-9]*?\]", input))
    if len(bib_references_found) < 5:
        bib_references_found = set(re.findall(r"\[.*?\]", input))

    res = {}
    for i in bib_references_found:
        bib_definitions_found = re.findall(rf"{re.escape(i)} +([^\[]*)", input)
        if bib_definitions_found:
            res[i] = bib_definitions_found[-1][:250]
            res[i] = " ".join(res[i].split())
            res[i] = res[i].replace("\n", " ")

    return res


def generate_json(input: str) -> str:
    return json.dumps(
        {
            "title": find_title(input),
            "versions": find_versions(input),
            "table_of_contents": [],
            "revisions": [],
            "bibliography": find_bibliography(input),
            "other": [],
        }, indent=4, ensure_ascii=False)


def generate_json_files(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf8") as file:
        input = file.read()

    output = generate_json(input)

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
