"""Integration tests for the full podcast generation pipeline."""

import tempfile
from pathlib import Path

import pytest

from src import audio_utils, text_processor, tts_client, wikipedia_client


class TestFullPipeline:
    """End-to-end integration tests."""

    def test_wikipedia_to_processed_text(self):
        """Test fetching Wikipedia content and preprocessing it."""
        # Fetch content
        content = wikipedia_client.get_page_content("Cornbread")
        assert len(content) > 100

        # Preprocess
        processed = text_processor.preprocess_text(content[:1000], context="test")  # Limit for speed
        assert len(processed) > 0
        assert isinstance(processed, str)

    def test_processed_text_to_audio(self):
        """Test converting processed text to audio."""
        # Simple preprocessed text
        text = "Cornbread is a traditional bread made from cornmeal."

        # Generate audio
        audio = tts_client.generate_audio(text, context="test")

        assert isinstance(audio, bytes)
        assert len(audio) > 1000  # Should be substantial

    def test_full_pipeline_small_article(self):
        """Test the complete pipeline with a small amount of text."""
        # Step 1: Fetch (using summary for speed)
        summary = wikipedia_client.get_page_summary("Cornbread")
        assert len(summary) > 50

        # Step 2: Preprocess
        processed = text_processor.preprocess_text(summary, context="test")
        assert len(processed) > 0

        # Step 3: Check balance
        has_balance, required, available = tts_client.check_sufficient_balance(processed)
        # We don't assert has_balance as it depends on account status
        assert required == len(processed)

        # Step 4: Generate audio (only if we have balance)
        if has_balance:
            audio = tts_client.generate_audio(processed, context="test")
            assert len(audio) > 0

            # Step 5: Save
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir) / "test_output.mp3"
                result = audio_utils.save_audio(audio, "cornbread", output_path)
                assert result.exists()
                assert result.stat().st_size > 0

    def test_chunking_and_concatenation(self):
        """Test that long text is properly chunked and audio concatenated."""
        # Create text that will need chunking
        text = "This is a test sentence. " * 200  # ~5000 characters

        # Chunk it
        chunks = audio_utils.chunk_text(text, chunk_size=1000)
        assert len(chunks) > 1

        # If we have balance, generate and concatenate
        has_balance, _, _ = tts_client.check_sufficient_balance(text)

        if has_balance:
            audio_segments = []
            for chunk in chunks[:2]:  # Only test first 2 chunks for speed
                audio = tts_client.generate_audio(chunk, context="test")
                audio_segments.append(audio)

            # Concatenate
            if len(audio_segments) > 1:
                combined = audio_utils.concatenate_audio(audio_segments)
                assert len(combined) > len(audio_segments[0])

    def test_preview_generation(self):
        """Test preview generation workflow."""
        # Get content
        content = wikipedia_client.get_page_content("Cornbread")

        # Preprocess a portion
        processed = text_processor.preprocess_text(content[:2000], context="test")

        # Check balance for preview
        preview_text = processed[:500]
        has_balance, _, _ = tts_client.check_sufficient_balance(preview_text)

        if has_balance:
            # Generate preview
            preview = tts_client.generate_preview(processed, char_count=500, context="test")

            assert isinstance(preview, bytes)
            assert len(preview) > 0

            # Save preview
            path = audio_utils.save_preview(preview, "cornbread")
            assert path.exists()

            # Cleanup
            path.unlink()


class TestErrorHandling:
    """Tests for error handling in the pipeline."""

    def test_nonexistent_wikipedia_page(self):
        """Test handling of nonexistent Wikipedia pages."""
        with pytest.raises(ValueError):
            wikipedia_client.get_page_content("ThisPageDefinitelyDoesNotExist12345")

    def test_empty_text_preprocessing(self):
        """Test preprocessing of empty text."""
        result = text_processor.preprocess_text("", context="test")

        # Should handle gracefully
        assert isinstance(result, str)

    def test_cost_estimation_accuracy(self):
        """Test that cost estimation is reasonable."""
        text = "x" * 1000

        # TTS cost should equal character count
        tts_cost = tts_client.estimate_cost(text)
        assert tts_cost == 1000

        # OpenAI cost should be small for this text
        openai_cost = text_processor.estimate_openai_cost(text)
        assert openai_cost < 0.01  # Should be fractions of a cent


class TestConfigIntegration:
    """Tests that configuration is properly loaded."""

    def test_api_keys_loaded(self):
        """Test that API keys are loaded from environment."""
        from src.config import ELEVENLABS_API_KEY, OPENAI_API_KEY

        # Keys should be loaded (not None or empty)
        # Note: This test will fail if .env is not configured
        assert OPENAI_API_KEY is not None
        assert ELEVENLABS_API_KEY is not None
        assert len(OPENAI_API_KEY) > 0
        assert len(ELEVENLABS_API_KEY) > 0

    def test_output_directory_exists(self):
        """Test that output directory is configured and exists."""
        from src.config import OUTPUT_DIR

        # Directory should exist or be creatable
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        assert OUTPUT_DIR.exists()
