"""Configuration settings for the podcast CLI."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of src directory)
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs settings
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - change after testing in playground
ELEVENLABS_MODEL_ID = "eleven_monolingual_v1"

# Audio settings
OUTPUT_DIR = Path(__file__).parent.parent / "output"
AUDIO_FORMAT = "mp3"

# Cache settings
CACHE_DIR = Path(__file__).parent.parent / "cache"

# Text processing settings
PREVIEW_CHAR_COUNT = 500  # Characters for preview generation
CHUNK_SIZE = 5000  # Max characters per TTS request

# Wikipedia settings
WIKIPEDIA_LANGUAGE = "en"
WIKIPEDIA_USER_AGENT = "podcast-cli/0.1.0 (https://github.com/dividing-by-zaro/podcast-cli)"
