"""Tests for audio utilities."""

import tempfile
from pathlib import Path

import pytest

from src.audio_utils import chunk_text, concatenate_audio, save_audio, save_preview
from src.config import CHUNK_SIZE


class TestChunkText:
    """Tests for text chunking functionality."""

    def test_short_text_returns_single_chunk(self):
        """Test that text shorter than chunk size returns one chunk."""
        text = "This is short text."
        chunks = chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_returns_multiple_chunks(self):
        """Test that long text is split into multiple chunks."""
        text = "This is a sentence. " * 500  # ~10,000 characters
        chunks = chunk_text(text, chunk_size=1000)

        assert len(chunks) > 1

    def test_chunks_respect_max_size(self):
        """Test that no chunk exceeds the maximum size."""
        text = "This is a sentence. " * 500
        chunk_size = 1000
        chunks = chunk_text(text, chunk_size=chunk_size)

        for chunk in chunks:
            assert len(chunk) <= chunk_size * 1.1  # Allow small overflow for sentence boundary

    def test_chunks_preserve_all_content(self):
        """Test that all content is preserved after chunking."""
        text = "Word " * 1000
        chunks = chunk_text(text, chunk_size=500)

        reconstructed = " ".join(chunks)
        # Allow for whitespace differences
        assert reconstructed.replace(" ", "") == text.replace(" ", "")

    def test_prefers_sentence_boundaries(self):
        """Test that chunks prefer to split at sentence boundaries."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunk_text(text, chunk_size=40)

        # Each chunk should ideally end with a period
        for chunk in chunks[:-1]:  # Except possibly the last
            assert chunk.strip().endswith(".") or chunk.strip().endswith(".")

    def test_handles_empty_string(self):
        """Test handling of empty input."""
        chunks = chunk_text("")

        assert chunks == [""]

    def test_handles_no_sentence_boundaries(self):
        """Test chunking text without sentence boundaries."""
        text = "word " * 1000  # No periods
        chunks = chunk_text(text, chunk_size=100)

        assert len(chunks) > 1
        # Should still produce valid chunks
        for chunk in chunks:
            assert len(chunk) > 0


class TestConcatenateAudio:
    """Tests for audio concatenation."""

    def test_single_segment_returns_unchanged(self):
        """Test that single segment is returned as-is."""
        segment = b"fake audio data"
        result = concatenate_audio([segment])

        assert result == segment

    def test_multiple_segments_concatenate(self):
        """Test that multiple segments are joined."""
        # This test requires valid MP3 data
        # For now, we'll just test the interface
        # Real test would need actual MP3 bytes
        pass  # TODO: Add with real MP3 test fixtures

    def test_returns_bytes(self):
        """Test that concatenation returns bytes."""
        segment = b"fake audio data"
        result = concatenate_audio([segment])

        assert isinstance(result, bytes)


class TestSaveAudio:
    """Tests for saving audio files."""

    def test_creates_file(self):
        """Test that save_audio creates a file."""
        audio_data = b"fake audio data"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.mp3"
            result = save_audio(audio_data, "test", output_path)

            assert result.exists()

    def test_returns_path(self):
        """Test that save_audio returns the file path."""
        audio_data = b"fake audio data"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.mp3"
            result = save_audio(audio_data, "test", output_path)

            assert isinstance(result, Path)
            assert result == output_path

    def test_writes_correct_content(self):
        """Test that file contains the correct audio data."""
        audio_data = b"fake audio data"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.mp3"
            save_audio(audio_data, "test", output_path)

            with open(output_path, "rb") as f:
                assert f.read() == audio_data

    def test_generates_filename_when_not_provided(self):
        """Test that filename is auto-generated when not provided."""
        audio_data = b"fake audio data"

        result = save_audio(audio_data, "Test Topic")

        assert result.exists()
        assert "test_topic" in result.name.lower()
        assert result.suffix == ".mp3"

        # Cleanup
        result.unlink()

    def test_handles_special_characters_in_topic(self):
        """Test that special characters in topic are sanitized."""
        audio_data = b"fake audio data"

        result = save_audio(audio_data, "Test/Topic:Special")

        assert result.exists()
        assert "/" not in result.name

        # Cleanup
        result.unlink()

    def test_creates_parent_directories(self):
        """Test that parent directories are created if needed."""
        audio_data = b"fake audio data"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dir" / "test.mp3"
            result = save_audio(audio_data, "test", output_path)

            assert result.exists()


class TestSavePreview:
    """Tests for saving preview audio files."""

    def test_creates_preview_file(self):
        """Test that save_preview creates a file."""
        audio_data = b"fake audio data"

        result = save_preview(audio_data, "Test Topic")

        assert result.exists()
        assert "preview" in result.name.lower()

        # Cleanup
        result.unlink()

    def test_preview_filename_includes_topic(self):
        """Test that preview filename includes the topic."""
        audio_data = b"fake audio data"

        result = save_preview(audio_data, "Cornbread")

        assert "cornbread" in result.name.lower()

        # Cleanup
        result.unlink()
