from common import parsed_fields_long, parsed_fields_short
import re
from typing import Dict, List, Tuple


def pretty_field_name(field: str) -> str:
    words = field.split("_")
    words = [word.title() if word != "of" else word for word in words]
    return " ".join(words)


def pretty_version_key(key: str) -> str:
    if len(key) == 3:
        return key.upper()
    else:
        splits = key.split("_")
        splits = [split.title() for split in splits]
        return "".join(splits)


def pretty_print_title(data: str):
    print(data)


def pretty_print_versions(data: Dict[str, List[str]]):
    labels_size = max(len(pretty_version_key(key)) for key in data.keys())
    
    for key, versions in sorted(data.items()):
        print(pretty_version_key(key).rjust(labels_size) + ":",
              ", ".join(versions),
              sep=" " * 4)


def pretty_print_table_of_contents(data: List[Tuple[str, str, int]]):
    col1_size = max(len(x[0]) for x in data)
    col2_size = max(len(x[1]) for x in data) + 4
    max_page_size = max(len(str(x[2])) for x in data)
    
    for id, title, page in data:
        title += " "
        print(id.ljust(col1_size) + " " * 3,
              title.ljust(col2_size + (max_page_size - len(str(page))), '.'),
              page)


def pretty_print_revisions(data: List[Dict[str, str]]):
    col1_title = "version"
    col2_title = "date"
    col3_title = "description"
    col1_size = max([len(x["version"]) for x in data] + [len(col1_title)])
    col2_size = max([len(x["date"]) for x in data] + [len(col2_title)])
    col3_size = max([len(x["description"]) for x in data] + [len(col3_title)])
    
    print(col1_title.rjust(col1_size),
          col2_title.ljust(col2_size),
          col3_title.ljust(col3_size),
          sep=" " * 4)
    
    for entry in data:
        print(entry["version"].rjust(col1_size),
              entry["date"].ljust(col2_size),
              entry["description"].ljust(col3_size),
              sep=" " * 4)


def pretty_print_bibliography(data: Dict[str, str]):
    if all(key[1:-1].isnumeric() for key in data.keys()):
        def sorting_key(key_value: Tuple[str, str]) -> List[int]:
            splits = re.split(r"_|-", key_value[0][1:-1])
            num_splits = [int(split) for split in splits]
            return num_splits
    else:
        def sorting_key(key_value: Tuple[str, str]) -> str:
            return key_value[0]

    labels_size = max(len(key) for key in data.keys())
    
    for key, text in sorted(data.items(), key=sorting_key):
        print(key.ljust(labels_size), text, sep=" " * 4)


def pretty_print(data, fields: List[str]):
    functions = {
        "title": pretty_print_title,
        "versions": pretty_print_versions,
        "table_of_contents": pretty_print_table_of_contents,
        "revisions": pretty_print_revisions,
        "bibliography": pretty_print_bibliography
    }

    for i, field in enumerate(fields):
        function = functions[field]
        
        if i != 0:
            print()
        print(pretty_field_name(field) + ":")
    
        function(data[field])

