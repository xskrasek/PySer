from common import deduplicate_list
import re
from typing import Dict, List


def parse_eal(input: str) -> List[str]:
    found = re.findall(r"[^\w](EAL ?[0-9]\+?)", input)

    return deduplicate_list(found)


def parse_sha(input: str) -> List[str]:
    versions = "512|384|256|224|3|2|1"

    input = input.replace(" ", "")
    found = re.findall(
        rf"SHA[-_ ]?(?:{versions})(?:[-/_ ](?:{versions}))?",
        input
    )

    return deduplicate_list(found)


def parse_des(input: str) -> List[str]:
    found = re.findall(r"3des", input, re.IGNORECASE)
    found += re.findall(r"des3", input, re.IGNORECASE)
    found += re.findall(r"triple[- ]des", input, re.IGNORECASE)
    found += re.findall(r"tdes", input, re.IGNORECASE)

    return deduplicate_list(found)


def parse_rsa(input: str) -> List[str]:
    versions = "4096|2048|1024"

    found = re.findall(
        rf"RSA[-_ ]?(?:{versions})(?:[-/_](?:{versions}))?",
        input
    )

    return deduplicate_list(found)


def parse_ecc(input: str) -> List[str]:
    found = re.findall(r"ECC", input)
    found += re.findall(r"ECC ?[0-9]+", input)
    for i in range(len(found)):
        found[i] = found[i].upper()

    return deduplicate_list(found)


def parse_global_platform(input: str) -> List[str]:
    found = re.findall(r"global ?platform (?:[0-9]\.)*[0-9]",
                       input, re.IGNORECASE)

    return deduplicate_list(found)


def parse_java_card(input: str) -> List[str]:
    found = re.findall(r"java ?card (?:[0-9]\.)*[0-9]",
                       input, re.IGNORECASE)

    return deduplicate_list(found)


def parse(input: str) -> Dict[str, List[str]]:
    versions = {}
    for (version_name, parse_function) in [
        ("eal", parse_eal),
        ("sha", parse_sha),
        ("des", parse_des),
        ("rsa", parse_rsa),
        ("ecc", parse_ecc),
        ("global_platform", parse_global_platform),
        ("java_card", parse_java_card)
    ]:
        result = parse_function(input)
        if result:
            versions[version_name] = result
    return versions
