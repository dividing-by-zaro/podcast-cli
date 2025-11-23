"""Main CLI entry point for podcast generation."""

import argparse
import sys
from pathlib import Path

from . import audio_utils, text_processor, tts_client, wikipedia_client
from .config import PREVIEW_CHAR_COUNT


def main():
    parser = argparse.ArgumentParser(
        description="Generate text-to-speech podcasts from Wikipedia articles"
    )
    parser.add_argument("topic", help="Wikipedia page title (e.g., 'Cornbread')")
    parser.add_argument(
        "-o", "--output", type=Path, help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "--auto", action="store_true", help="Skip preview confirmation"
    )
    parser.add_argument(
        "--preview-only", action="store_true", help="Generate preview only"
    )

    args = parser.parse_args()

    # Step 1: Check if Wikipedia page exists
    print(f"Checking Wikipedia for '{args.topic}'...")
    if not wikipedia_client.page_exists(args.topic):
        print(f"Error: Wikipedia page '{args.topic}' not found.")
        sys.exit(1)
    print("✓ Page found")

    # Step 2: Fetch content
    print("Fetching article content...")
    content = wikipedia_client.get_page_content(args.topic)
    print(f"✓ Retrieved {len(content):,} characters")

    # Step 3: Preprocess with OpenAI
    print("Preprocessing text for TTS...")
    processed_text = text_processor.preprocess_text(content)
    print(f"✓ Processed to {len(processed_text):,} characters")

    # Step 4: Check ElevenLabs balance
    print("Checking ElevenLabs account balance...")
    has_balance, required, available = tts_client.check_sufficient_balance(processed_text)
    print(f"  Required: {required:,} characters")
    print(f"  Available: {available:,} characters")

    if not has_balance:
        print(f"Error: Insufficient balance. Need {required - available:,} more characters.")
        sys.exit(1)
    print("✓ Sufficient balance")

    # Step 5: Generate preview
    if not args.auto:
        print(f"\nGenerating {PREVIEW_CHAR_COUNT}-character preview...")
        preview_audio = tts_client.generate_preview(processed_text, PREVIEW_CHAR_COUNT)
        preview_path = audio_utils.save_preview(preview_audio, args.topic)
        print(f"✓ Preview saved to: {preview_path}")

        if args.preview_only:
            print("\nPreview generation complete.")
            sys.exit(0)

        # Ask for confirmation
        response = input("\nContinue with full generation? [y/N]: ").strip().lower()
        if response != "y":
            print("Generation cancelled.")
            sys.exit(0)

    # Step 6: Generate full audio
    print("\nGenerating full audio...")
    chunks = audio_utils.chunk_text(processed_text)
    print(f"  Split into {len(chunks)} chunk(s)")

    audio_segments = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  Processing chunk {i}/{len(chunks)}...")
        audio = tts_client.generate_audio(chunk)
        audio_segments.append(audio)

    # Step 7: Concatenate and save
    print("Concatenating audio segments...")
    final_audio = audio_utils.concatenate_audio(audio_segments)

    output_path = audio_utils.save_audio(final_audio, args.topic, args.output)
    print(f"\n✓ Podcast saved to: {output_path}")


if __name__ == "__main__":
    main()
