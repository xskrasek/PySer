from common import squash_whitespace
import re


def parse_dirty(input: str) -> str:
    iter = re.search(r"title:?\s+([^\n]*)",
                     input, re.IGNORECASE | re.MULTILINE)
    if iter:
        potential_title_count = squash_whitespace(input).count(iter.group(1))
        if potential_title_count > 5:
            return iter.group(1)

    # Arbitrary limit, title after 1000 characters would be weird.
    input = input[:1000]

    # For documents starting with 4 numbers only.
    iter = re.search(r"for\s\s+(.*?)\s\s+from",
                     input.replace("\n", " "), re.MULTILINE)
    if iter:
        return iter.group(1)

    # e.g. NSCIB-CC-217812-CR2
    iter = re.search(
        r"Version [0-9]+-[0-9]+\s*(([^\n]+\n)*)", input, re.MULTILINE)
    if iter:
        return iter.group(1)

    # e.g. nscib-cc-0229286sscdkeygen-stv1.2
    if "NXP " in input:
        iter = re.search(r"([^\n]+\n)+", input, re.MULTILINE | re.DOTALL)
        if iter:
            return iter.group(0)

    # e.g. 0782V5b_pdf
    iter = re.search(r"security target[^\n]*(.*)common criteria",
                     input, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    if iter and len(squash_whitespace(iter.group(1))) > 5:
        return iter.group(1)

    # e.g. 1110V3b_pdf
    iter = re.search(r"\n\n([^\n].+?\n)\n\n", input, re.MULTILINE | re.DOTALL)
    if iter:
        return iter.group(1)

    # Last resort.
    iter = re.search(r"([^\n]+\n)*", input, re.MULTILINE)
    if iter:
        return iter.group(0)

    return ""


def parse(input: str) -> str:
    title = parse_dirty(input)

    index = title.lower().find("security target lite")
    if index > 0:
        title = title[:index]

    title = squash_whitespace(title)
    return title
