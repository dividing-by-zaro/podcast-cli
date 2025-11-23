"""Text preprocessing using OpenAI for TTS optimization."""

from openai import OpenAI

from .config import OPENAI_API_KEY

PREPROCESSING_PROMPT = """You are a text preprocessor optimizing content for text-to-speech.

Apply these transformations to the input text:
1. Convert Arabic numerals to written words (e.g., "1" → "one", "1990" → "nineteen ninety")
2. Expand common acronyms for pronunciation (e.g., "USA" → "U.S.A.", "NASA" → "NASA" is fine)
3. Expand abbreviations (e.g., "Dr." → "Doctor", "etc." → "et cetera")
4. Replace semicolons with periods for natural pauses
5. Remove or rephrase parenthetical asides that sound awkward when spoken
6. Simplify overly complex sentences for better listening comprehension
7. Remove citation markers like [1], [2], etc.

Return ONLY the processed text with no explanations or commentary."""


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client."""
    return OpenAI(api_key=OPENAI_API_KEY)


def preprocess_text(text: str) -> str:
    """
    Preprocess text for optimal text-to-speech output.

    Uses OpenAI to convert numerals, expand acronyms, and improve readability.

    Args:
        text: The raw text to preprocess.

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
