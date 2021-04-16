from typing import List


def squash_whitespace(input: str) -> str:
    return " ".join(input.split()).replace("\n", " ")


def deduplicate_list(input: List) -> List:
    return list(set(input))

