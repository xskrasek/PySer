import title_parser
import versions_parser
import table_of_contents_parser
import revisions_parser
import bibliography_parser


def parse(input: str):
    return {
        "title": title_parser.parse(input),
        "versions": versions_parser.parse(input),
        "table_of_contents": table_of_contents_parser.parse(input),
        "revisions": revisions_parser.parse(input),
        "bibliography": bibliography_parser.parse(input),
        "other": [],
    }
