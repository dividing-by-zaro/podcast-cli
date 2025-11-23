"""Prepend intro to an existing audio file."""

import sys
from pathlib import Path

from pydub import AudioSegment

INTRO_PATH = Path(__file__).parent.parent / "assets" / "intro.mp3"


def prepend_intro_to_file(audio_path: Path) -> None:
    """Prepend intro to an existing audio file, overwriting it."""
    if not INTRO_PATH.exists():
        print(f"Error: Intro file not found at {INTRO_PATH}")
        sys.exit(1)

    if not audio_path.exists():
        print(f"Error: Audio file not found at {audio_path}")
        sys.exit(1)

    print(f"Loading intro from: {INTRO_PATH}")
    intro = AudioSegment.from_mp3(INTRO_PATH)

    print(f"Loading audio from: {audio_path}")
    main_audio = AudioSegment.from_mp3(audio_path)

    print("Prepending intro...")
    combined = intro + main_audio

    print(f"Saving to: {audio_path}")
    combined.export(audio_path, format="mp3")

    print(f"\n✓ Intro prepended successfully")
    print(f"  Original duration: {len(main_audio) / 1000:.1f}s")
    print(f"  Intro duration: {len(intro) / 1000:.1f}s")
    print(f"  New duration: {len(combined) / 1000:.1f}s")


if __name__ == "__main__":
    # Prepend to the cornbread episode
    cornbread_path = Path(__file__).parent.parent / "output" / "cornbread_20251123_114302.mp3"
    prepend_intro_to_file(cornbread_path)
