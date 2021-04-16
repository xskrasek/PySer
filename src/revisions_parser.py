import re
from typing import Dict, List


def parse(input: str) -> List[Dict[str, str]]:
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

