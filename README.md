A CLI tool that generates text-to-speech podcasts from Wikipedia articles.

## Features

- Fetches Wikipedia articles via the Wikipedia API
- Preprocesses text with OpenAI for optimal TTS (numerals → words, acronyms, readability)
- Generates audio using ElevenLabs TTS
- Preview functionality before full generation
- Automatic chunking for long articles
- Cost estimation and balance checking
- Usage logging to track API costs

## Requirements

- Python 3.13+
- ffmpeg (for audio concatenation)
- OpenAI API key
- ElevenLabs API key

## Installation

```bash
# Clone the repository
git clone https://github.com/dividing-by-zaro/podcast-cli.git
cd podcast-cli

# Install dependencies with uv
uv sync

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
# Generate podcast with preview confirmation
uv run python -m src.main "Cornbread"

# Skip preview, generate immediately
uv run python -m src.main "Cornbread" --auto

# Preview only (no full generation)
uv run python -m src.main "Cornbread" --preview-only

# Specify output filename
uv run python -m src.main "Cornbread" -o output/my_podcast.mp3

# View usage/cost report
uv run python -m src.main --usage
```

## Configuration

Edit `src/config.py` to customize:

- `ELEVENLABS_VOICE_ID` - Voice to use for TTS
- `PREVIEW_CHAR_COUNT` - Characters for preview (default: 500)
- `CHUNK_SIZE` - Max characters per TTS request (default: 5000)

## Project Structure

```
podcast-cli/
├── src/
│   ├── main.py             # CLI entry point
│   ├── config.py           # Settings
│   ├── wikipedia_client.py # Wikipedia API
│   ├── text_processor.py   # OpenAI preprocessing
│   ├── tts_client.py       # ElevenLabs TTS
│   ├── audio_utils.py      # Audio handling
│   └── usage_logger.py     # API cost tracking
├── tests/                  # Test suite
├── output/                 # Generated audio files
└── logs/                   # Usage logs (gitignored)
```

## License

MIT
