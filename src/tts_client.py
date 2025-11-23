"""ElevenLabs TTS client for audio generation."""

from elevenlabs import ElevenLabs

from .config import ELEVENLABS_API_KEY, ELEVENLABS_MODEL_ID, ELEVENLABS_VOICE_ID


def get_elevenlabs_client() -> ElevenLabs:
    """Create and return an ElevenLabs client."""
    return ElevenLabs(api_key=ELEVENLABS_API_KEY)


def get_account_balance() -> float:
    """
    Get the current ElevenLabs account character balance.

    Returns:
        The number of characters remaining in the account.
    """
    client = get_elevenlabs_client()
    subscription = client.user.get_subscription()
    return subscription.character_limit - subscription.character_count


def estimate_cost(text: str) -> int:
    """
    Estimate the character cost for generating audio.

    Args:
        text: The text to be converted to speech.

    Returns:
        The number of characters that will be consumed.
    """
    return len(text)


def check_sufficient_balance(text: str) -> tuple[bool, int, int]:
    """
    Check if account has sufficient balance for the text.

    Args:
        text: The text to be converted to speech.

    Returns:
        Tuple of (has_sufficient_balance, required_chars, available_chars).
    """
    required = estimate_cost(text)
    available = get_account_balance()
    return available >= required, required, int(available)


def generate_audio(text: str, voice_id: str | None = None) -> bytes:
    """
    Generate audio from text using ElevenLabs TTS.

    Args:
        text: The text to convert to speech.
        voice_id: Optional voice ID override.

    Returns:
        The audio data as bytes.
    """
    client = get_elevenlabs_client()
    voice = voice_id or ELEVENLABS_VOICE_ID

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=ELEVENLABS_MODEL_ID,
    )

    # Convert generator to bytes
    audio_bytes = b"".join(audio)
    return audio_bytes


def generate_preview(text: str, char_count: int = 500) -> bytes:
    """
    Generate a preview audio clip from the beginning of the text.

    Args:
        text: The full text.
        char_count: Number of characters for the preview.

    Returns:
        The preview audio data as bytes.
    """
    preview_text = text[:char_count]

    # Try to end at a sentence boundary
    last_period = preview_text.rfind(".")
    if last_period > char_count * 0.5:
        preview_text = preview_text[: last_period + 1]

    return generate_audio(preview_text)
