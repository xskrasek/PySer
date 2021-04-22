import re
from typing import Dict, List


def month_to_number(input: str) -> str:
    values = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }
    form = input[:3].lower()
    if form in values:
        return values[form]
    return input


def clean_date(input: str) -> str:
    if not input:
        return ""

    splitted = re.split("\.|-", input)
    if len(splitted) != 3:
        return input

    # swap year and day
    if int(splitted[0]) < 1000:
        splitted.reverse()

    # use number for months
    splitted[1] = month_to_number(splitted[1])

    return "-".join(splitted)


def parse_general(input: str, regex: str, ver_index: int, date_index: int) -> List[Dict[str, str]]:
    end = re.search(r"\n{4}", input, re.IGNORECASE)
    input = input[:end.span(0)[1]] if end else input[:5000]

    results = re.findall(regex, input)

    final_results = []
    for result in results:
        version = result[ver_index]
        date = clean_date(result[date_index])
        # there can be more information, like author...
        description = result[2].split("  ")[-1]

        final_results.append({
            "version": version,
            "date": date,
            "description": description,
        })
    return final_results


REVISION_EX = r"v?([0-9.]+)"
DATE_EX = r"([0-9-A-Za-z-\.]+)"


def parse_rev_date_desc(input: str) -> List[Dict[str, str]]:
    return parse_general(input,
                         rf"\s+{REVISION_EX}\s+{DATE_EX}?[\s:]\s+(.*)",
                         0, 1)


def parse_date_ver_desc(input: str) -> List[Dict[str, str]]:
    return parse_general(input,
                         rf"\s+{DATE_EX}?\s+{REVISION_EX}[\s:]\s+(.*)",
                         1, 0)


def parse(input: str) -> List[Dict[str, str]]:
    found = re.search(r"^\w*rev\w*\s+date\s+.*description",
                      input, re.IGNORECASE | re.MULTILINE)
    if found:
        return parse_rev_date_desc(input[found.span(0)[1]:])

    found = re.search(r"date\s+ver\w*\s+.*description", input, re.IGNORECASE)
    if found:
        return parse_date_ver_desc(input[found.span(0)[1]:])

    found = re.search(r"version\s\s+description", input, re.IGNORECASE)
    if found:
        return parse_rev_date_desc(input[found.span(0)[1]:])

    # final attempt, filtering out capitalization that could be used in normal text
    iter = re.finditer(r"REVISION HISTORY|Revision [Hh]istory"
                       r"|VERSION CONTROL|Version [Cc]ontrol", input)
    iter_list = list(iter)
    if iter_list:
        # first mention probably in toc, so take the second one, if there is one
        if len(iter_list) < 2:
            start = iter_list[0]
        else:
            start = iter_list[1]

        return parse_rev_date_desc(input[start.span(0)[1]:])

    return []
