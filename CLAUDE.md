# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

CLI tool that converts Wikipedia articles into audio podcasts. Given a topic (e.g., "Cornbread"), it fetches the Wikipedia article, preprocesses the text for better TTS output (converting numerals to words, expanding abbreviations), and generates an MP3 using ElevenLabs text-to-speech.

## Build & Run Commands

```bash
# Install dependencies
uv sync --extra dev

# Run the CLI
uv run python -m src.main "Topic"

# Run all tests
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_wikipedia_client.py -v

# Run a specific test
uv run pytest tests/test_wikipedia_client.py::TestPageExists::test_existing_page_returns_true -v

# View usage/cost report
uv run python -m src.main --usage
```

## Architecture

### Pipeline Flow

The application follows a linear pipeline:

1. **Wikipedia fetch** (`wikipedia_client.py`) - Validates page exists, retrieves content
2. **Text preprocessing** (`text_processor.py`) - OpenAI converts numerals to words, expands abbreviations, removes citations
3. **Balance check** (`tts_client.py`) - Verifies ElevenLabs account has sufficient characters
4. **Audio generation** (`tts_client.py`) - Converts text to speech, with optional preview
5. **Audio processing** (`audio_utils.py`) - Chunks long text, concatenates audio segments, saves files

### Usage Logging

All API calls are logged to `logs/usage.jsonl` with:
- Token/character counts and costs
- Context ("test" or "production")
- Topic name

When calling `preprocess_text()`, `generate_audio()`, or `generate_preview()`, pass `context="test"` in tests to separate test costs from production.

### Configuration

API keys loaded from `.env` via `config.py`. Key settings:
- `ELEVENLABS_VOICE_ID` - Change after testing voices in ElevenLabs playground
- `CHUNK_SIZE` - Max characters per TTS request (default 5000)
- `PREVIEW_CHAR_COUNT` - Characters for preview generation (default 500)

## Known Issues

- `.env` file not loading during pytest runs (path resolution issue)
- Requires Python 3.13+ due to `audioop-lts` dependency for pydub compatibility
- ffmpeg required for audio concatenation
