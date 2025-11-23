"""Main CLI entry point for podcast generation."""

import argparse
import sys
from pathlib import Path

from . import audio_utils, cache, text_processor, tts_client, wikipedia_client
from .config import PREVIEW_CHAR_COUNT
from .usage_logger import print_usage_report


def main():
    parser = argparse.ArgumentParser(
        description="Generate text-to-speech podcasts from Wikipedia articles"
    )
    parser.add_argument(
        "topic", nargs="?", help="Wikipedia page title (e.g., 'Cornbread')"
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "--auto", action="store_true", help="Skip preview confirmation"
    )
    parser.add_argument(
        "--preview-only", action="store_true", help="Generate preview only"
    )
    parser.add_argument(
        "--usage", action="store_true", help="Show usage report and exit"
    )
    parser.add_argument(
        "--cache-only", action="store_true", help="Fetch and preprocess only, save to cache without TTS"
    )
    parser.add_argument(
        "--from-cache", action="store_true", help="Generate audio from cached preprocessed text"
    )
    parser.add_argument(
        "--list-cache", action="store_true", help="List all cached topics and exit"
    )

    args = parser.parse_args()

    # Handle usage report
    if args.usage:
        print_usage_report()
        sys.exit(0)

    # Handle list cache
    if args.list_cache:
        cached_topics = cache.list_cached()
        if cached_topics:
            print("Cached topics:")
            for topic in sorted(cached_topics):
                print(f"  - {topic}")
        else:
            print("No cached topics found.")
        sys.exit(0)

    # Validate topic is provided for generation
    if not args.topic:
        parser.error("topic is required for podcast generation")

    # Handle --from-cache: load preprocessed text from cache
    if args.from_cache:
        if not cache.is_cached(args.topic):
            print(f"Error: Topic '{args.topic}' is not cached.")
            print("Use --list-cache to see available cached topics.")
            sys.exit(1)

        print(f"Loading '{args.topic}' from cache...")
        processed_text = cache.load_from_cache(args.topic)
        print(f"✓ Loaded {len(processed_text):,} characters from cache")

        # Skip to TTS generation (Step 4 onwards)
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
            preview_audio = tts_client.generate_preview(
                processed_text, PREVIEW_CHAR_COUNT, context="production", topic=args.topic
            )
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
            audio = tts_client.generate_audio(
                chunk, context="production", topic=args.topic
            )
            audio_segments.append(audio)

        # Step 7: Concatenate and save
        print("Concatenating audio segments...")
        final_audio = audio_utils.concatenate_audio(audio_segments)

        output_path = audio_utils.save_audio(final_audio, args.topic, args.output)
        print(f"\n✓ Podcast saved to: {output_path}")
        sys.exit(0)

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
    processed_text = text_processor.preprocess_text(
        content, context="production", topic=args.topic
    )
    print(f"✓ Processed to {len(processed_text):,} characters")

    # Handle --cache-only: save to cache and exit
    if args.cache_only:
        cache_path = cache.save_to_cache(args.topic, processed_text)
        print(f"\n✓ Cached preprocessed text to: {cache_path}")
        print(f"  Use --from-cache '{args.topic}' to generate audio later.")
        sys.exit(0)

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
        preview_audio = tts_client.generate_preview(
            processed_text, PREVIEW_CHAR_COUNT, context="production", topic=args.topic
        )
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
        audio = tts_client.generate_audio(
            chunk, context="production", topic=args.topic
        )
        audio_segments.append(audio)

    # Step 7: Concatenate and save
    print("Concatenating audio segments...")
    final_audio = audio_utils.concatenate_audio(audio_segments)

    output_path = audio_utils.save_audio(final_audio, args.topic, args.output)
    print(f"\n✓ Podcast saved to: {output_path}")


if __name__ == "__main__":
    main()
