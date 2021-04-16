from common import squash_whitespace
import re


def parse_dirty(input: str) -> str:
    # Arbitrary limit, title after 1000 characters would be weird.
    input = input[:1000]

    # For documents starting with 4 numbers only.
    iter = re.search(r"for\s\s+(.*?)\s\s+from",
                     input.replace("\n", " "), re.MULTILINE)
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


def parse(input: str) -> str:
    title = parse_dirty(input)
    title = squash_whitespace(title)
    return title

