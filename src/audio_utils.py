"""Audio utilities for chunking, concatenation, and file saving."""

import io
from datetime import datetime
from pathlib import Path

from pydub import AudioSegment

from .config import AUDIO_FORMAT, CHUNK_SIZE, OUTPUT_DIR

# Path to the intro audio file
INTRO_PATH = Path(__file__).parent.parent / "assets" / "intro.mp3"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Split text into chunks for TTS processing.

    Attempts to split at sentence boundaries to maintain natural flow.

    Args:
        text: The text to split.
        chunk_size: Maximum characters per chunk.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= chunk_size:
            chunks.append(remaining)
            break

        # Find a good split point
        chunk = remaining[:chunk_size]

        # Try to split at sentence boundary
        last_period = chunk.rfind(". ")
        last_newline = chunk.rfind("\n")

        split_point = max(last_period, last_newline)

        if split_point > chunk_size * 0.5:
            chunk = remaining[: split_point + 1]

        chunks.append(chunk.strip())
        remaining = remaining[len(chunk) :].strip()

    return chunks


def concatenate_audio(audio_segments: list[bytes]) -> bytes:
    """
    Concatenate multiple audio segments into one.

    Args:
        audio_segments: List of audio data as bytes.

    Returns:
        Combined audio data as bytes.
    """
    if len(audio_segments) == 1:
        return audio_segments[0]

    combined = AudioSegment.empty()

    for segment_bytes in audio_segments:
        segment = AudioSegment.from_mp3(io.BytesIO(segment_bytes))
        combined += segment

    # Export to bytes
    output_buffer = io.BytesIO()
    combined.export(output_buffer, format=AUDIO_FORMAT)
    return output_buffer.getvalue()


def save_audio(audio_data: bytes, topic: str, output_path: Path | None = None) -> Path:
    """
    Save audio data to a file.

    Args:
        audio_data: The audio data as bytes.
        topic: The topic name for filename generation.
        output_path: Optional custom output path.

    Returns:
        The path where the file was saved.
    """
    if output_path is None:
        # Generate filename: {topic}_{timestamp}.mp3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.lower().replace(" ", "_").replace("/", "_")
        filename = f"{safe_topic}_{timestamp}.{AUDIO_FORMAT}"
        output_path = OUTPUT_DIR / filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(audio_data)

    return output_path


def save_preview(audio_data: bytes, topic: str) -> Path:
    """
    Save preview audio to a temporary file.

    Args:
        audio_data: The preview audio data.
        topic: The topic name.

    Returns:
        The path where the preview was saved.
    """
    safe_topic = topic.lower().replace(" ", "_").replace("/", "_")
    filename = f"{safe_topic}_preview.{AUDIO_FORMAT}"
    output_path = OUTPUT_DIR / filename

    return save_audio(audio_data, topic, output_path)


def prepend_intro(audio_data: bytes) -> bytes:
    """
    Prepend the intro audio to the given audio data.

    Args:
        audio_data: The main audio data as bytes.

    Returns:
        Combined audio with intro prepended.
    """
    if not INTRO_PATH.exists():
        print(f"Warning: Intro file not found at {INTRO_PATH}")
        return audio_data

    # Load intro and main audio
    intro = AudioSegment.from_mp3(INTRO_PATH)
    main_audio = AudioSegment.from_mp3(io.BytesIO(audio_data))

    # Combine intro + main audio
    combined = intro + main_audio

    # Export to bytes
    output_buffer = io.BytesIO()
    combined.export(output_buffer, format=AUDIO_FORMAT)
    return output_buffer.getvalue()
