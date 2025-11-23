"""Text preprocessing using OpenAI for TTS optimization."""

from openai import OpenAI

from .config import OPENAI_API_KEY
from .usage_logger import log_openai_usage

PREPROCESSING_PROMPT = """You are a text preprocessor optimizing content for ElevenLabs text-to-speech.

Apply these transformations to the input text:

## 1. Pauses and Pacing
- Use em-dashes (—) or double dashes (--) for natural pauses between thoughts
- For longer pauses (e.g., section breaks), use: <break time="1.5s" />
- Replace semicolons with periods for natural pauses

## 2. Number & Text Normalization
- Convert all numerals to written words:
  - Cardinal: "123" → "one hundred twenty-three"
  - Ordinal: "2nd" → "second"
  - Years: "1990" → "nineteen ninety"
  - Decimals: "3.5" → "three point five"
  - Fractions: "⅔" → "two-thirds"
- Monetary values: "$45.67" → "forty-five dollars and sixty-seven cents"
- Phone numbers: "123-456-7890" → "one two three, four five six, seven eight nine zero"
- Dates: "2024-01-01" → "January first, two thousand twenty-four"
- Times: "14:30" → "two thirty PM"

## 3. Abbreviations & Acronyms
- Expand all abbreviations: "Dr." → "Doctor", "Ave." → "Avenue", "etc." → "et cetera"
- Expand units: "100km" → "one hundred kilometers", "TB" → "terabyte"
- For acronyms that should be spelled out, add spaces: "HTTP" → "H T T P"
- Common acronyms that are pronounced as words can stay: "NASA", "NATO"

## 4. Special Characters & Symbols
- Percentages: "100%" → "one hundred percent"
- Email addresses: "user@example.com" → "user at example dot com"
- URLs: "example.com/page" → "example dot com slash page"
- Mathematical symbols: "+" → "plus", "=" → "equals", "&" → "and"

## 5. General Cleanup
- Remove citation markers like [1], [2], etc.
- Remove or rephrase parenthetical asides that sound awkward when spoken
- Simplify overly complex sentences for better listening comprehension

Return ONLY the processed text with no explanations or commentary."""


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client."""
    return OpenAI(api_key=OPENAI_API_KEY)


def preprocess_text(
    text: str,
    context: str = "production",
    topic: str | None = None,
) -> str:
    """
    Preprocess text for optimal text-to-speech output.

    Uses OpenAI to convert numerals, expand acronyms, and improve readability.

    Args:
        text: The raw text to preprocess.
        context: "production" or "test" for usage logging.
        topic: Optional topic name for usage logging.

    Returns:
        The preprocessed text optimized for TTS.
    """
    client = get_openai_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PREPROCESSING_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )

    # Log usage
    usage = response.usage
    if usage:
        log_openai_usage(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            model="gpt-4o-mini",
            context=context,
            topic=topic,
        )

    return response.choices[0].message.content


def estimate_openai_cost(text: str) -> float:
    """
    Estimate the OpenAI API cost for preprocessing text.

    Args:
        text: The text to be processed.

    Returns:
        Estimated cost in USD.
    """
    # Rough estimate: 1 token ≈ 4 characters
    input_tokens = len(text) / 4
    output_tokens = input_tokens * 1.2  # Output slightly larger due to expansions

    # gpt-4o-mini pricing (as of 2024)
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60

    return input_cost + output_cost
