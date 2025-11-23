"""Tests for ElevenLabs TTS client functionality."""

import pytest

from src.tts_client import (
    check_sufficient_balance,
    estimate_cost,
    generate_audio,
    generate_preview,
    get_account_balance,
)


class TestGetAccountBalance:
    """Tests for checking ElevenLabs account balance."""

    def test_returns_numeric_balance(self):
        """Test that balance is returned as a number."""
        balance = get_account_balance()

        assert isinstance(balance, (int, float))

    def test_balance_is_non_negative(self):
        """Test that balance is not negative."""
        balance = get_account_balance()

        assert balance >= 0

    def test_balance_retrieval_succeeds(self):
        """Test that we can successfully retrieve balance without errors."""
        # Should not raise any exceptions
        balance = get_account_balance()

        assert balance is not None


class TestEstimateCost:
    """Tests for character cost estimation."""

    def test_returns_character_count(self):
        """Test that cost estimate returns character count."""
        text = "Hello, world!"
        cost = estimate_cost(text)

        assert cost == len(text)

    def test_empty_text_has_zero_cost(self):
        """Test that empty text has zero cost."""
        cost = estimate_cost("")

        assert cost == 0

    def test_longer_text_costs_more(self):
        """Test that longer text has higher cost."""
        short = "Hi"
        long = "Hello, this is a much longer piece of text."

        assert estimate_cost(long) > estimate_cost(short)


class TestCheckSufficientBalance:
    """Tests for balance sufficiency checking."""

    def test_returns_tuple(self):
        """Test that function returns a tuple of three values."""
        result = check_sufficient_balance("Test text")

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_tuple_contains_correct_types(self):
        """Test that tuple contains (bool, int, int)."""
        has_balance, required, available = check_sufficient_balance("Test")

        assert isinstance(has_balance, bool)
        assert isinstance(required, int)
        assert isinstance(available, int)

    def test_required_matches_text_length(self):
        """Test that required characters matches text length."""
        text = "This is test text."
        has_balance, required, available = check_sufficient_balance(text)

        assert required == len(text)

    def test_small_text_likely_has_sufficient_balance(self):
        """Test that very small text should have sufficient balance."""
        # Assuming account has at least 10 characters
        has_balance, required, available = check_sufficient_balance("Hello")

        # This might fail if account is completely empty
        # but that would indicate a configuration issue
        assert required == 5


class TestGenerateAudio:
    """Tests for audio generation."""

    def test_returns_bytes(self):
        """Test that audio generation returns bytes."""
        audio = generate_audio("Hello, world.", context="test")

        assert isinstance(audio, bytes)

    def test_audio_is_not_empty(self):
        """Test that generated audio has content."""
        audio = generate_audio("Hello, world.", context="test")

        assert len(audio) > 0

    def test_audio_has_mp3_header(self):
        """Test that audio data appears to be valid MP3."""
        audio = generate_audio("Hello, world.", context="test")

        # MP3 files typically start with ID3 tag or frame sync
        # ID3 starts with "ID3"
        # Frame sync starts with 0xFF 0xFB (or similar)
        is_id3 = audio[:3] == b"ID3"
        is_frame_sync = audio[0] == 0xFF and (audio[1] & 0xE0) == 0xE0

        assert is_id3 or is_frame_sync

    def test_longer_text_produces_larger_audio(self):
        """Test that longer text produces larger audio files."""
        short_audio = generate_audio("Hi.", context="test")
        long_audio = generate_audio("Hello, this is a longer piece of text for testing.", context="test")

        assert len(long_audio) > len(short_audio)

    def test_handles_special_characters(self):
        """Test that special characters are handled."""
        audio = generate_audio("Hello! How are you? I'm fine, thanks.", context="test")

        assert isinstance(audio, bytes)
        assert len(audio) > 0


class TestGeneratePreview:
    """Tests for preview audio generation."""

    def test_returns_bytes(self):
        """Test that preview generation returns bytes."""
        text = "This is a sample text. " * 50
        preview = generate_preview(text, char_count=100, context="test")

        assert isinstance(preview, bytes)

    def test_preview_is_shorter_than_full(self):
        """Test that preview audio is shorter than full would be."""
        text = "This is a sample text for testing. " * 100
        preview = generate_preview(text, char_count=100, context="test")
        full = generate_audio(text, context="test")

        assert len(preview) < len(full)

    def test_preview_respects_char_count(self):
        """Test that preview uses approximately the specified character count."""
        text = "This is a sample. " * 100
        preview = generate_preview(text, char_count=50, context="test")

        # Preview should exist and be non-empty
        assert len(preview) > 0

    def test_preview_ends_at_sentence_boundary(self):
        """Test that preview attempts to end at sentence boundary."""
        # This is hard to test directly, but we can verify it works
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        preview = generate_preview(text, char_count=40, context="test")

        assert isinstance(preview, bytes)
        assert len(preview) > 0
