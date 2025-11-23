"""Tests for text preprocessing with OpenAI."""

import pytest

from src.text_processor import estimate_openai_cost, preprocess_text


class TestPreprocessText:
    """Tests for OpenAI text preprocessing."""

    def test_converts_numerals_to_words(self):
        """Test that Arabic numerals are converted to written words."""
        text = "There are 3 types of cornbread."
        result = preprocess_text(text, context="test")

        # Should not contain the numeral "3"
        assert "3" not in result
        # Should contain "three" or similar written form
        assert "three" in result.lower()

    def test_converts_years_to_spoken_form(self):
        """Test that years are converted to speakable format."""
        text = "Cornbread originated in 1492."
        result = preprocess_text(text, context="test")

        # Should not contain "1492" as numerals
        assert "1492" not in result

    def test_expands_abbreviations(self):
        """Test that common abbreviations are expanded."""
        text = "Dr. Smith studied cornbread, etc."
        result = preprocess_text(text, context="test")

        # "Dr." should become "Doctor"
        assert "Dr." not in result
        # "etc." should be expanded
        assert "etc." not in result

    def test_removes_citation_markers(self):
        """Test that citation markers like [1] are removed."""
        text = "Cornbread is popular[1] in the South[2]."
        result = preprocess_text(text, context="test")

        assert "[1]" not in result
        assert "[2]" not in result

    def test_handles_acronyms(self):
        """Test that acronyms are handled for pronunciation."""
        text = "The USA loves cornbread from the FDA approved recipe."
        result = preprocess_text(text, context="test")

        # Result should still be readable and make sense
        assert len(result) > 0
        assert "cornbread" in result.lower()

    def test_simplifies_complex_sentences(self):
        """Test that overly complex sentences are simplified."""
        text = "Cornbread; which is made from cornmeal; has been a staple; particularly in Southern cuisine; for centuries."
        result = preprocess_text(text, context="test")

        # Semicolons should be converted to periods or simplified
        # The result should have fewer semicolons
        assert result.count(";") < text.count(";")

    def test_preserves_meaning(self):
        """Test that preprocessing preserves the core meaning."""
        text = "Cornbread is a traditional bread made from cornmeal."
        result = preprocess_text(text, context="test")

        # Key words should still be present
        assert "cornbread" in result.lower()
        assert "cornmeal" in result.lower()

    def test_handles_empty_string(self):
        """Test handling of empty input."""
        result = preprocess_text("", context="test")

        # Should return something (even if empty or minimal)
        assert isinstance(result, str)

    def test_handles_long_text(self):
        """Test processing of longer text passages."""
        text = "Cornbread is delicious. " * 100
        result = preprocess_text(text, context="test")

        assert len(result) > 0
        assert isinstance(result, str)


class TestEstimateOpenAICost:
    """Tests for OpenAI cost estimation."""

    def test_returns_float(self):
        """Test that cost estimate returns a float."""
        cost = estimate_openai_cost("Sample text")

        assert isinstance(cost, float)

    def test_longer_text_costs_more(self):
        """Test that longer text has higher estimated cost."""
        short_text = "Hello"
        long_text = "Hello " * 1000

        short_cost = estimate_openai_cost(short_text)
        long_cost = estimate_openai_cost(long_text)

        assert long_cost > short_cost

    def test_empty_text_has_minimal_cost(self):
        """Test that empty text has near-zero cost."""
        cost = estimate_openai_cost("")

        assert cost >= 0
        assert cost < 0.01

    def test_cost_is_reasonable(self):
        """Test that estimated cost is in a reasonable range."""
        # 10,000 characters should cost less than $1
        text = "x" * 10000
        cost = estimate_openai_cost(text)

        assert cost < 1.0
        assert cost > 0
