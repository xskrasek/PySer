from typing import List


parsed_fields_long = [
    "title", "versions", "table_of_contents", "revisions", "bibliography"
]
parsed_fields_short = ["tit", "ver", "toc", "rev", "bib"]


def squash_whitespace(input: str) -> str:
    return " ".join(input.split()).replace("\n", " ")


def deduplicate_list(input: List) -> List:
    return list(set(input))
