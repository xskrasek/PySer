from typing import List


parsed_fields_long = [
    "title", "versions", "table_of_contents", "revisions", "bibliography"
]
parsed_fields_short = ["tit", "ver", "toc", "rev", "bib"]


def squash_whitespace(plain_text: str) -> str:
    return " ".join(plain_text.split()).replace("\n", " ")


def deduplicate_list(plain_text: List) -> List:
    return list(set(plain_text))
