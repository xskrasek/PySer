from common import squash_whitespace
import re
import itertools
from operator import itemgetter
from typing import List, Tuple


def postprocess_match(match: Tuple[str, str, str]) -> Tuple[str, str, int]:
    id, title, page_str = tuple(group.strip() for group in match)
    if id.endswith("."):
        # For some reason there are not dots at the end in the dataset.
        id = id[:-1]
    title = squash_whitespace(title)
    page = int(page_str)
    return id, title, page


def parse_table(input_original: str) -> List[Tuple[str, str, int]]:
    # Look at the start and the end of document.
    start = 0.15
    end = -start
    input = input_original[:int(len(input_original) * start)] + \
            input_original[int(len(input_original) * end):]

    # TOC with dots
    matches = re.findall(r"(?<!Table )"
                         r"([A-D1-9][0-9.]*)" # chapter
                         r" +"
                         r"([A-Z][^\.]+)" # title
                         r" ?(?:(?:\.){2,}|(?:\.\s){2,}) ?" # dots
                         r"([0-9]+)", # page
                         input)

    # TOC without dots
    if not matches:
        matches = re.findall(r"([A-D0-9][0-9.]*)" # chapter
                             r" +"
                             r"(.*)" #r"(.*[^\s].*)" # title
                             r" {5,}"
                             r"([0-9]+)", # page
                             input)

    # Postprocess the matches
    result = list(map(postprocess_match, matches))
    return result


def sort(result: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
    def sorting_key(toc_entry: Tuple[str, str, int]) -> List[int]:
        def val(toc_id: str) -> int:
            if toc_id.isdigit():
                return int(toc_id)
            else:
                return ord(toc_id) - ord('A') + 100
    
        return [val(id) for id in toc_entry[0].split(".")]

    if any([r[0].isalpha() for r in result]):
        # worth 4 points
        splits: List[List[Tuple[str, str, int]]] = [[]]

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


def parse(input: str) -> List[Tuple[str, str, int]]:
    result = parse_table(input)
    result = sort(result)
    return result

