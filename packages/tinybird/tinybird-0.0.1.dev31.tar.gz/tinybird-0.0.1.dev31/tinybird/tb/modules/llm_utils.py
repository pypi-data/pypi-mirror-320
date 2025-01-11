import re
from typing import List


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""


def parse_xml(text: str, tag: str) -> List[str]:
    """
    Parses the text for the specified XML tag and returns a list of the contents of each tag.
    """
    return re.findall(f"<{tag}.*?>(.*?)</{tag}>", text, re.DOTALL)
