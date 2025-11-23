"""Cache management for preprocessed Wikipedia articles."""

import re
from pathlib import Path

from .config import CACHE_DIR


def get_cache_dir() -> Path:
    """
    Get the cache directory path, creating it if necessary.

    Returns:
        Path to the cache directory.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def _normalize_filename(topic: str) -> str:
    """
    Normalize topic name to a safe filename.

    Args:
        topic: The topic name.

    Returns:
        A filesystem-safe filename.
    """
    # Replace spaces and special characters with underscores
    normalized = re.sub(r'[^\w\-]', '_', topic)
    # Remove consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)
    # Strip leading/trailing underscores
    normalized = normalized.strip('_')
    return normalized.lower()


def get_cache_path(topic: str) -> Path:
    """
    Get the cache file path for a topic.

    Args:
        topic: The topic name.

    Returns:
        Path to the cache file.
    """
    filename = f"{_normalize_filename(topic)}.txt"
    return get_cache_dir() / filename


def save_to_cache(topic: str, text: str) -> Path:
    """
    Save preprocessed text to cache.

    Args:
        topic: The topic name.
        text: The preprocessed text to cache.

    Returns:
        Path to the saved cache file.
    """
    cache_path = get_cache_path(topic)
    cache_path.write_text(text, encoding='utf-8')
    return cache_path


def load_from_cache(topic: str) -> str:
    """
    Load preprocessed text from cache.

    Args:
        topic: The topic name.

    Returns:
        The cached preprocessed text.

    Raises:
        ValueError: If the topic is not cached.
    """
    cache_path = get_cache_path(topic)

    if not cache_path.exists():
        raise ValueError(f"Topic '{topic}' is not cached.")

    return cache_path.read_text(encoding='utf-8')


def is_cached(topic: str) -> bool:
    """
    Check if a topic is cached.

    Args:
        topic: The topic name.

    Returns:
        True if the topic is cached, False otherwise.
    """
    return get_cache_path(topic).exists()


def list_cached() -> list[str]:
    """
    List all cached topic names.

    Returns:
        List of cached topic names (derived from filenames).
    """
    cache_dir = get_cache_dir()
    cached = []

    for cache_file in cache_dir.glob("*.txt"):
        # Convert filename back to topic name (approximate)
        topic = cache_file.stem.replace('_', ' ').title()
        cached.append(topic)

    return cached


def delete_from_cache(topic: str) -> bool:
    """
    Delete a topic from cache.

    Args:
        topic: The topic name.

    Returns:
        True if deleted, False if topic was not cached.
    """
    cache_path = get_cache_path(topic)

    if cache_path.exists():
        cache_path.unlink()
        return True

    return False


def clear_cache() -> int:
    """
    Clear all cached topics.

    Returns:
        Number of cache files deleted.
    """
    cache_dir = get_cache_dir()
    count = 0

    for cache_file in cache_dir.glob("*.txt"):
        cache_file.unlink()
        count += 1

    return count
