"""Tests for Wikipedia article caching functionality."""

import tempfile
from pathlib import Path

import pytest

from src import cache


class TestCacheOperations:
    """Tests for basic cache save/load operations."""

    def test_save_and_load_text(self, tmp_path, monkeypatch):
        """Test that saved text can be loaded back correctly."""
        # Use temporary directory for cache
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topic = "Cornbread"
        text = "Cornbread is a traditional bread made from cornmeal."

        # Save to cache
        cache.save_to_cache(topic, text)

        # Load from cache
        loaded = cache.load_from_cache(topic)

        assert loaded == text

    def test_is_cached_returns_true_for_existing(self, tmp_path, monkeypatch):
        """Test that is_cached returns True for cached topics."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topic = "TestTopic"
        text = "Some test content."

        cache.save_to_cache(topic, text)

        assert cache.is_cached(topic) is True

    def test_is_cached_returns_false_for_missing(self, tmp_path, monkeypatch):
        """Test that is_cached returns False for non-cached topics."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        assert cache.is_cached("NonExistentTopic") is False

    def test_load_nonexistent_raises_error(self, tmp_path, monkeypatch):
        """Test that loading non-cached topic raises ValueError."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        with pytest.raises(ValueError):
            cache.load_from_cache("NonExistentTopic")

    def test_list_cached_returns_all_topics(self, tmp_path, monkeypatch):
        """Test that list_cached returns all cached topic names."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topics = ["Cornbread", "Pizza", "Sushi"]
        for topic in topics:
            cache.save_to_cache(topic, f"Content about {topic}")

        cached = cache.list_cached()

        assert set(cached) == set(topics)

    def test_delete_from_cache_removes_topic(self, tmp_path, monkeypatch):
        """Test that delete_from_cache removes the cached topic."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topic = "ToDelete"
        cache.save_to_cache(topic, "Some content")
        assert cache.is_cached(topic) is True

        cache.delete_from_cache(topic)

        assert cache.is_cached(topic) is False

    def test_cache_preserves_unicode(self, tmp_path, monkeypatch):
        """Test that cache correctly handles unicode characters."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topic = "Unicode"
        text = "日本語テスト 中文测试 émojis: 🎉🎊"

        cache.save_to_cache(topic, text)
        loaded = cache.load_from_cache(topic)

        assert loaded == text

    def test_cache_normalizes_topic_names(self, tmp_path, monkeypatch):
        """Test that topic names are normalized for filesystem safety."""
        monkeypatch.setattr(cache, "get_cache_dir", lambda: tmp_path)

        topic = "Topic With Spaces"
        text = "Content here"

        cache.save_to_cache(topic, text)

        # Should be able to load with same topic name
        loaded = cache.load_from_cache(topic)
        assert loaded == text


class TestCacheDirectory:
    """Tests for cache directory management."""

    def test_get_cache_dir_creates_directory(self, tmp_path, monkeypatch):
        """Test that get_cache_dir creates the directory if it doesn't exist."""
        from src import config

        cache_path = tmp_path / "test_cache"
        monkeypatch.setattr(config, "CACHE_DIR", cache_path)

        # Reload the function to use new config
        result = cache.get_cache_dir()

        assert result.exists()
        assert result.is_dir()
