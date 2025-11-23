"""Usage logging for tracking API costs."""

import json
from datetime import datetime
from pathlib import Path

from .config import OUTPUT_DIR

# Log file location
LOGS_DIR = OUTPUT_DIR.parent / "logs"
USAGE_LOG_FILE = LOGS_DIR / "usage.jsonl"

# Pricing (as of late 2024)
OPENAI_PRICING = {
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,   # $0.15 per 1M input tokens
        "output": 0.60 / 1_000_000,  # $0.60 per 1M output tokens
    }
}

ELEVENLABS_PRICING = {
    # Approximate cost per character (varies by plan)
    # Free tier: ~10,000 chars/month
    # Starter: $5/month for 30,000 chars = $0.000167/char
    # Creator: $22/month for 100,000 chars = $0.00022/char
    "per_character": 0.000167,  # Using Starter tier estimate
}


def _ensure_log_dir():
    """Ensure the logs directory exists."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_openai_usage(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o-mini",
    context: str = "production",
    topic: str | None = None,
):
    """
    Log OpenAI API usage.

    Args:
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens used.
        model: The model used.
        context: "production" or "test".
        topic: Optional topic/article name.
    """
    _ensure_log_dir()

    pricing = OPENAI_PRICING.get(model, OPENAI_PRICING["gpt-4o-mini"])
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    total_cost = input_cost + output_cost

    entry = {
        "timestamp": datetime.now().isoformat(),
        "service": "openai",
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(total_cost, 6),
        "context": context,
        "topic": topic,
    }

    with open(USAGE_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def log_elevenlabs_usage(
    characters: int,
    context: str = "production",
    topic: str | None = None,
):
    """
    Log ElevenLabs API usage.

    Args:
        characters: Number of characters converted to speech.
        context: "production" or "test".
        topic: Optional topic/article name.
    """
    _ensure_log_dir()

    cost = characters * ELEVENLABS_PRICING["per_character"]

    entry = {
        "timestamp": datetime.now().isoformat(),
        "service": "elevenlabs",
        "characters": characters,
        "cost_usd": round(cost, 6),
        "context": context,
        "topic": topic,
    }

    with open(USAGE_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def get_usage_summary(context: str | None = None) -> dict:
    """
    Get a summary of all usage.

    Args:
        context: Filter by "production" or "test". None for all.

    Returns:
        Summary dict with totals for each service.
    """
    if not USAGE_LOG_FILE.exists():
        return {
            "openai": {"total_tokens": 0, "total_cost_usd": 0, "calls": 0},
            "elevenlabs": {"total_characters": 0, "total_cost_usd": 0, "calls": 0},
            "total_cost_usd": 0,
        }

    openai_tokens = 0
    openai_cost = 0
    openai_calls = 0
    elevenlabs_chars = 0
    elevenlabs_cost = 0
    elevenlabs_calls = 0

    with open(USAGE_LOG_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)

            if context and entry.get("context") != context:
                continue

            if entry["service"] == "openai":
                openai_tokens += entry.get("total_tokens", 0)
                openai_cost += entry.get("cost_usd", 0)
                openai_calls += 1
            elif entry["service"] == "elevenlabs":
                elevenlabs_chars += entry.get("characters", 0)
                elevenlabs_cost += entry.get("cost_usd", 0)
                elevenlabs_calls += 1

    return {
        "openai": {
            "total_tokens": openai_tokens,
            "total_cost_usd": round(openai_cost, 4),
            "calls": openai_calls,
        },
        "elevenlabs": {
            "total_characters": elevenlabs_chars,
            "total_cost_usd": round(elevenlabs_cost, 4),
            "calls": elevenlabs_calls,
        },
        "total_cost_usd": round(openai_cost + elevenlabs_cost, 4),
    }


def get_usage_by_topic() -> dict:
    """
    Get usage grouped by topic.

    Returns:
        Dict mapping topic names to their usage summaries.
    """
    if not USAGE_LOG_FILE.exists():
        return {}

    topics = {}

    with open(USAGE_LOG_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            topic = entry.get("topic") or "unknown"

            if topic not in topics:
                topics[topic] = {"openai_cost": 0, "elevenlabs_cost": 0, "total_cost": 0}

            cost = entry.get("cost_usd", 0)
            if entry["service"] == "openai":
                topics[topic]["openai_cost"] += cost
            else:
                topics[topic]["elevenlabs_cost"] += cost
            topics[topic]["total_cost"] += cost

    # Round values
    for topic in topics:
        for key in topics[topic]:
            topics[topic][key] = round(topics[topic][key], 4)

    return topics


def clear_logs():
    """Clear all usage logs."""
    if USAGE_LOG_FILE.exists():
        USAGE_LOG_FILE.unlink()


def print_usage_report():
    """Print a formatted usage report to console."""
    summary = get_usage_summary()
    test_summary = get_usage_summary(context="test")
    prod_summary = get_usage_summary(context="production")

    print("\n" + "=" * 50)
    print("USAGE REPORT")
    print("=" * 50)

    print("\n📊 Overall Totals:")
    print(f"  OpenAI: {summary['openai']['total_tokens']:,} tokens (${summary['openai']['total_cost_usd']:.4f})")
    print(f"  ElevenLabs: {summary['elevenlabs']['total_characters']:,} chars (${summary['elevenlabs']['total_cost_usd']:.4f})")
    print(f"  Total Cost: ${summary['total_cost_usd']:.4f}")

    if test_summary["total_cost_usd"] > 0:
        print("\n🧪 Test Usage:")
        print(f"  OpenAI: ${test_summary['openai']['total_cost_usd']:.4f}")
        print(f"  ElevenLabs: ${test_summary['elevenlabs']['total_cost_usd']:.4f}")

    if prod_summary["total_cost_usd"] > 0:
        print("\n🚀 Production Usage:")
        print(f"  OpenAI: ${prod_summary['openai']['total_cost_usd']:.4f}")
        print(f"  ElevenLabs: ${prod_summary['elevenlabs']['total_cost_usd']:.4f}")

    topics = get_usage_by_topic()
    if topics:
        print("\n📝 By Topic:")
        for topic, costs in sorted(topics.items(), key=lambda x: x[1]["total_cost"], reverse=True):
            print(f"  {topic}: ${costs['total_cost']:.4f}")

    print("\n" + "=" * 50)
