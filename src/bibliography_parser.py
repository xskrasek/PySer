from common import squash_whitespace
import re
from typing import Dict


def parse(input: str) -> Dict[str, str]:
    references_found = set(re.findall(r"\[[0-9]*-?[0-9]*?\]", input))
    if len(references_found) < 5:
        references_found = set(re.findall(r"\[.*?\]", input))

    result = {}
    for i in references_found:
        definitions_found = re.findall(rf"{re.escape(i)} +([^\[]*)", input)
        if definitions_found:
            result[i] = definitions_found[-1][:250]
            result[i] = squash_whitespace(result[i])

    return result
