"""Generate the permanent intro audio for Food for Sleep podcast."""

from pathlib import Path

from src.tts_client import generate_audio, check_sufficient_balance

INTRO_TEXT = (
    "Welcome to Food for Sleep, your forever ad-free podcast to help you rest. "
    "You're doing something wonderful for your health by prioritizing sleep, "
    "and we're here to support you. Now, we wish you a peaceful sleep."
)


def main():
    # Check balance first
    has_balance, required, available = check_sufficient_balance(INTRO_TEXT)
    print(f"Required: {required} characters")
    print(f"Available: {available} characters")

    if not has_balance:
        print("Error: Insufficient balance")
        return

    print("\nGenerating intro audio...")
    audio_bytes = generate_audio(
        text=INTRO_TEXT,
        context="production",
        topic="intro",
    )

    # Save to assets directory
    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    output_path = assets_dir / "intro.mp3"
    output_path.write_bytes(audio_bytes)

    print(f"\nIntro saved to: {output_path}")
    print(f"File size: {len(audio_bytes):,} bytes")


if __name__ == "__main__":
    main()
