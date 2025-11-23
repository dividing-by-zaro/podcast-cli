"""Wikipedia API client for fetching article content."""

import wikipediaapi

from .config import WIKIPEDIA_LANGUAGE, WIKIPEDIA_USER_AGENT


def get_wikipedia_client() -> wikipediaapi.Wikipedia:
    """Create and return a Wikipedia API client."""
    return wikipediaapi.Wikipedia(
        user_agent=WIKIPEDIA_USER_AGENT,
        language=WIKIPEDIA_LANGUAGE,
    )


def normalize_topic(topic: str) -> str:
    """Normalize topic case to match Wikipedia title format."""
    return topic.title()


def page_exists(topic: str) -> bool:
    """Check if a Wikipedia page exists for the given topic."""
    wiki = get_wikipedia_client()
    page = wiki.page(normalize_topic(topic))
    return page.exists()


def get_page_content(topic: str) -> str:
    """
    Fetch the full text content of a Wikipedia page.

    Args:
        topic: The Wikipedia page title to fetch.

    Returns:
        The full text content of the page.

    Raises:
        ValueError: If the page does not exist.
    """
    wiki = get_wikipedia_client()
    normalized = normalize_topic(topic)
    page = wiki.page(normalized)

    if not page.exists():
        raise ValueError(f"Wikipedia page '{topic}' does not exist.")

    return page.text


def get_page_summary(topic: str) -> str:
    """
    Fetch just the summary of a Wikipedia page.

    Args:
        topic: The Wikipedia page title to fetch.

    Returns:
        The summary text of the page.

    Raises:
        ValueError: If the page does not exist.
    """
    wiki = get_wikipedia_client()
    normalized = normalize_topic(topic)
    page = wiki.page(normalized)

    if not page.exists():
        raise ValueError(f"Wikipedia page '{topic}' does not exist.")

    return page.summary
