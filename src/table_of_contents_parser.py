from common import squash_whitespace
import re
import itertools
from operator import itemgetter
from typing import List, Tuple, Optional


def find_dotted_toc(input: str) -> Optional[str]:
    def is_dotted_line(line: str) -> bool:
        return len(line) >= 20 and line.count('.') >= len(line) * 0.1

    lines = input.split('\n')
    dot_lines = [i for i in range(len(lines)) if is_dotted_line(lines[i])]

    if len(dot_lines) == 0:
        return None

    dot_lines_med = dot_lines[len(dot_lines) // 2]

    def is_outlier(line: int) -> bool:
        return abs(line - dot_lines_med) > 1.5 * len(dot_lines)

    dot_lines = [line for line in dot_lines if not is_outlier(line)]
    margin = 30
    start = max(0, dot_lines[0] - margin)
    end = min(len(lines), dot_lines[-1] + margin)
    return "\n".join(lines[start:end])


def postprocess_match(match: Tuple[str, str, str, str]) -> Optional[Tuple[str, str, int]]:
    if match[0] is not None and len(match[0]) != 0:
        return None

    id, title, page_str = tuple(group.strip() for group in match[1:])
    title = squash_whitespace(title)
    page = int(page_str)
    return id, title, page


def postprocess_matches(matches: List[Tuple[str, str, str, str]]) -> List[Tuple[str, str, int]]:
    return list([r for r in map(postprocess_match, matches) if r is not None])


def parse_without_dots(input_original: str) -> List[Tuple[str, str, int]]:
    # Look at the start and the end of the document
    start = 0.15
    end = -start
    input = input_original[:int(len(input_original) * start)] + \
            input_original[int(len(input_original) * end):]

    matches = re.findall(r"((?:Table|Figure|(?:Fig|Tab)\.?) |[^\s1-9])?" # manual negative lookbehind
                         r"([A-D1-9][0-9]?(?:\.[0-9]{1,2})*)\.?" # section number
                         r" {1,20}"
                         r"(.*)" #r"(.*[^\s].*)" # title
                         r" {5,}"
                         r"([0-9]+)", # page number
                         input)

    return postprocess_matches(matches) if matches is not None else []


def parse_with_dots(input: str) -> List[Tuple[str, str, int]]:
    matches = re.findall(r"((?:Table|Figure|(?:Fig|Tab)\.?) |[^\s1-9])?" # manual negative lookbehind
                         r"([A-D1-9][0-9]?(?:\.[0-9]{1,2})*)\.?" # section number
                         r" {1,20}"
                         r"([A-Z](?:[^\.](?! {6,})|\.(?! ?\.))+)" # title
                         r" ?(?:(?:\.){2,}|(?:\.\s){2,}) ?" # dots
                         r"([0-9]+)", # page number
                         input, re.MULTILINE)

    return postprocess_matches(matches) if matches is not None else []


def parse_with_dots_multiple_columns(input: str):
    lines = input.split("\n")

    regex = re.compile(r"((?:Table|Figure|(?:Fig|Tab)\.?) |[^\s1-9])?" # manual negative lookbehind
                       r"([A-D1-9][0-9]?(?:\.[0-9]{1,2})*)\.?" # section number
                       r" {1,20}"
                       r"([A-Z](?:[^\.](?! {6,})|\.(?! ?\.))+)" # title
                       r" ?(?:(?:\.){2,}|(?:\.\s){2,}) ?" # dots
                       r"([0-9]+)") # page number
    
    matches = []
    left_column = ""
    right_column = ""

    for line in lines:
        match_iter = regex.finditer(line)

        try:
            match = next(match_iter)
            lookbehind, id, title, page = match.groups()
            matches.append((lookbehind, id, title, page))
            left_column += squash_whitespace(line[:match.start()]) + '\n'
            right_column += squash_whitespace(line[match.end():]) + '\n'
        except StopIteration:
            # NOTE: This is the weak point. We have tried counting in also the surrounding page
            # and section numbers.
            spaces = list(re.finditer(r"\s{2,}", line))
            if len(spaces) != 0:
                largest_space = max(spaces, key=lambda match: match.end() - match.start())
                left_column += squash_whitespace(line[:largest_space.start()]) + '\n'
                right_column += squash_whitespace(line[largest_space.end():]) + '\n'

    result = postprocess_matches(matches)
    result += parse_with_dots(left_column)
    result += parse_with_dots(right_column)
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
        # Sort only locally inbetween alphabetical chapter IDs
        splits: List[List[Tuple[str, str, int]]] = [[]]

        for r in result:
            splits[-1].append(r)
            if r[0].isalpha():
                splits.append([])

        splits = [sorted(split, key=sorting_key) for split in splits]
        result = list(itertools.chain.from_iterable(splits))
    else:
        # Sort globally
        result = sorted(result, key=sorting_key)

    return result


def parse(input: str) -> List[Tuple[str, str, int]]:
    dotted_toc = find_dotted_toc(input)

    if dotted_toc is not None:
        result = parse_with_dots(dotted_toc)
        result = parse_with_dots_multiple_columns(dotted_toc)
    else:
        result = parse_without_dots(input)

    result = sort(result)
    return result

