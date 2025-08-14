from typing import Optional


def safe_text(element, default: Optional[str] = "-"):
    """
    Return stripped text from an element, or a default value if None or empty.

    Args:
        element: An element object (e.g., from BeautifulSoup or lxml) or None.
        default (str): Value to return if element is None or has no text.

    Returns:
        str: The stripped text content of the element, or the default value.
    """
    if element is not None and element.text:
        return element.text.strip()
    return default
