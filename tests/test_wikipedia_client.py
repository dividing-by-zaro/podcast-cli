"""Tests for Wikipedia client functionality."""

import pytest

from src.wikipedia_client import get_page_content, get_page_summary, page_exists


class TestPageExists:
    """Tests for checking if Wikipedia pages exist."""

    def test_existing_page_returns_true(self):
        """Test that a known Wikipedia page is found."""
        assert page_exists("Cornbread") is True

    def test_nonexistent_page_returns_false(self):
        """Test that a nonsense page title returns False."""
        assert page_exists("Xyzzy123NonexistentPage456") is False

    def test_page_with_special_characters(self):
        """Test page lookup with special characters."""
        # "C++" is a valid Wikipedia page
        assert page_exists("C++") is True

    def test_case_sensitivity(self):
        """Test that page lookup handles case correctly."""
        # Wikipedia normalizes case for the first letter
        assert page_exists("cornbread") is True
        assert page_exists("CORNBREAD") is True


class TestGetPageContent:
    """Tests for fetching full page content."""

    def test_fetches_content_for_valid_page(self):
        """Test that content is fetched for a valid page."""
        content = get_page_content("Cornbread")

        assert content is not None
        assert len(content) > 100
        assert isinstance(content, str)

    def test_content_contains_expected_text(self):
        """Test that fetched content contains relevant information."""
        content = get_page_content("Cornbread")

        # Content should mention corn or maize
        content_lower = content.lower()
        assert "corn" in content_lower or "maize" in content_lower

    def test_raises_error_for_nonexistent_page(self):
        """Test that ValueError is raised for nonexistent pages."""
        with pytest.raises(ValueError) as exc_info:
            get_page_content("Xyzzy123NonexistentPage456")

        assert "does not exist" in str(exc_info.value)

    def test_content_has_no_html_tags(self):
        """Test that returned content is plain text without HTML."""
        content = get_page_content("Cornbread")

        assert "<div" not in content
        assert "<p>" not in content
        assert "</a>" not in content


class TestGetPageSummary:
    """Tests for fetching page summaries."""

    def test_fetches_summary_for_valid_page(self):
        """Test that summary is fetched for a valid page."""
        summary = get_page_summary("Cornbread")

        assert summary is not None
        assert len(summary) > 50
        assert isinstance(summary, str)

    def test_summary_is_shorter_than_full_content(self):
        """Test that summary is shorter than full article."""
        summary = get_page_summary("Cornbread")
        content = get_page_content("Cornbread")

        assert len(summary) < len(content)

    def test_raises_error_for_nonexistent_page(self):
        """Test that ValueError is raised for nonexistent pages."""
        with pytest.raises(ValueError) as exc_info:
            get_page_summary("Xyzzy123NonexistentPage456")

        assert "does not exist" in str(exc_info.value)
