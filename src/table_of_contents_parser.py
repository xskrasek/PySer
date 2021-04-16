from common import squash_whitespace
import re
import itertools
from operator import itemgetter
from typing import List, Tuple


def parse_table(input_original: str) -> List[List[str]]:
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

    return result


def sort(result: List[List[str]]):
    def sorting_key(toc_entry: List[str]) -> List[int]:
        def val(toc_id: str) -> int:
            if toc_id.isdigit():
                return int(toc_id)
            else:
                return ord(toc_id) - ord('A') + 100
    
        return [val(id) for id in toc_entry[0].split(".")]

    if any([r[0].isalpha() for r in result]):
        # worth 4 points
        splits: List[List[List[str]]] = [[]]

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


def parse(input: str) -> List[List[str]]:
    result = parse_table(input)
    result = sort(result)
    return result

