import json
import re
from typing import Dict, List


def deduplicate_list(input: List) -> List:
    return list(set(input))


def find_title_dirty(input: str) -> str:
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


def find_title(input: str) -> str:
    title = find_title_dirty(input)
    title = " ".join(title.split())
    return title


def find_eal(input: str) -> List[str]:
    found = re.findall(r"EAL ?[0-9]\+?", input)

    return deduplicate_list(found)


def find_sha(input: str) -> List[str]:
    versions = "512|384|256|224|3|2|1"

    input = input.replace(" ", "")
    found = re.findall(
        rf"SHA[-_ ]?(?:{versions})(?:[-/_ ](?:{versions}))?",
        input
    )

    return deduplicate_list(found)


def find_des(input: str) -> List[str]:
    found = re.findall(r"3des", input, re.IGNORECASE)
    found += re.findall(r"triple-des", input, re.IGNORECASE)
    found += re.findall(r"tdes", input, re.IGNORECASE)

    return deduplicate_list(found)


def find_rsa(input: str) -> List[str]:
    versions = "4096|2048|1024"

    found = re.findall(
        rf"RSA[-_ ]?(?:{versions})(?:[-/_](?:{versions}))?",
        input
    )

    return deduplicate_list(found)


def find_ecc(input: str) -> List[str]:
    found = re.findall(r"ECC", input)
    found += re.findall(r"ECC ?[0-9]+", input)
    for i in range(len(found)):
        found[i] = found[i].upper()

    return deduplicate_list(found)


def find_versions(input: str) -> Dict[str, List[str]]:
    versions = {}
    for (version_name, parse_function) in [("eal", find_eal),
                                           ("sha", find_sha),
                                           ("des", find_des),
                                           ("rsa", find_rsa),
                                           ("ecc", find_ecc)]:
        result = parse_function(input)
        if result:
            versions[version_name] = result
    return versions


def find_bibliography(input: str) -> Dict[str, str]:
    references_found = set(re.findall(r"\[[0-9]*-?[0-9]*?\]", input))
    if len(references_found) < 5:
        references_found = set(re.findall(r"\[.*?\]", input))

    result = {}
    for i in references_found:
        definitions_found = re.findall(rf"{re.escape(i)} +([^\[]*)", input)
        if definitions_found:
            result[i] = definitions_found[-1][:250]
            result[i] = " ".join(result[i].split())
            result[i] = result[i].replace("\n", " ")

    return result


def find_table_of_contents(input_original: str) -> List[List[str]]:
    # Look at the start and the end of document.
    input = input_original[:20000] + input_original[-10000:]

    # TOC with dots
    result = re.findall(r"([A-Z0-9.]+) +([^\.]+) ?\.\.\.\.+ ?([0-9]+)", input)

    # TOC without dots
    if not result:
        result = re.findall(r"([0-9.]+) +(.*)     +([0-9]+)", input)

    # Clean up the result
    for i in range(len(result)):
        result[i] = list(result[i])
        for j in range(3):
            result[i][j] = result[i][j].strip()
        if result[i][0][-1] == '.':
            # For some reason there are not dots at the end in the dataset.
            result[i][0] = result[i][0][:-1]
        result[i][2] = int(result[i][2])

    return result


def find_revisions(input: str) -> List[Dict[str, str]]:
    # find start
    iter = re.finditer(r"revision history|version control", input, re.IGNORECASE)
    start = None
    a = 0
    for start in iter:
        a += 1
        # first mention probably in toc
        if a == 2:
            break
    if not start:
        return []
    input = input[start.span(0)[1]:]

    # find end
    end = re.search(r"\n\n\n\n", input, re.IGNORECASE)
    if end:
        input = input[:end.span(0)[1]]
    else:
        input = input[:5000]
    
    result = re.findall(r"\s+([0-9.]+)\s+([0-9-]+)?\s+(.*)", input)
    
    for i in range(len(result)):
        result[i] = {
            "version": result[i][0],
            "date": result[i][1],
            # there can be more information, like author...
            "description": result[i][2].split("  ")[-1],
        }

    return result

def generate_json(input: str) -> str:
    return json.dumps(
        {
            "title": find_title(input),
            "versions": find_versions(input),
            "table_of_contents": find_table_of_contents(input),
            "revisions": find_revisions(input),
            "bibliography": find_bibliography(input),
            "other": [],
        }, indent=4, ensure_ascii=False)
