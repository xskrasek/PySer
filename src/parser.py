import json
import re
from operator import itemgetter
from typing import Dict, List

import collections
import itertools


def squash_whitespace(input: str) -> str:
    return " ".join(input.split()).replace("\n", " ")


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
    title = squash_whitespace(title)
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
            result[i] = squash_whitespace(result[i])

    return result


def find_table_of_contents(input_original: str) -> List[List[str]]:
    # Look at the start and the end of document.
    start = 0.15
    end = -start
    input = input_original[:int(len(input_original) * start)] + \
            input_original[int(len(input_original) * end):]

    # TOC with dots
    result = re.findall(r"(?<!Table )"
                        r"([A-D1-9][0-9.]*)" # chapter
                        r" +"
                        r"([A-Z][^\.]+)" # title
                        r" ?(?:(?:\.){2,}|(?:\.\s){2,}) ?" # dots
                        r"([0-9]+)", # page
                        input)

    # TOC without dots
    if not result:
        result = re.findall(r"([A-D0-9][0-9.]*)" # chapter
                            r" +"
                            r"(.*)" #r"(.*[^\s].*)" # title
                            r" {5,}"
                            r"([0-9]+)", # page
                            input)

    # Clean up the result
    for i in range(len(result)):
        result[i] = [group.strip() for group in result[i]]
        if result[i][0].endswith("."):
            # For some reason there are not dots at the end in the dataset.
            result[i][0] = result[i][0][:-1]
        result[i][1] = squash_whitespace(result[i][1])
        result[i][2] = int(result[i][2])

    def sorting_key(toc_entry: List[str]) -> List[int]:
        def val(toc_id):
            if toc_id.isdigit():
                return int(toc_id)
            else:
                return ord(toc_id) - ord('A') + 100
    
        return [val(id) for id in toc_entry[0].split(".")]

    if any([r[0].isalpha() for r in result]):
        # worth 4 points
        splits = [[]]

        for r in result:
            splits[-1].append(r)
            if r[0].isalpha():
                splits.append([])

        splits = [sorted(split, key=sorting_key) for split in splits]
        result = list(itertools.chain.from_iterable(splits))
    else:
        # worth 8 points
        result = sorted(result, key=sorting_key)

    return result


def find_revisions(input: str) -> List[Dict[str, str]]:
    # find start
    iter = re.finditer(r"revision history|version control", input,
                       re.IGNORECASE)
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
    end = re.search(r"\n{4}", input, re.IGNORECASE)
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

