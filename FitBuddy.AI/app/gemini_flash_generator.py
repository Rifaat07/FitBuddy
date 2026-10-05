from google import genai
from google.genai import types

from .config import settings


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to the .env file before generating an AI tip."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_nutrition_tip_with_flash(
    *,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy.AI, a helpful fitness and nutrition assistant.

User fitness goal: {goal}
Workout intensity: {intensity}

Give the user one short, practical nutrition or healthy-lifestyle tip
that supports their fitness goal.

Requirements:
- Keep it concise.
- Make it practical.
- Avoid medical claims.
- Do not prescribe medication or supplements.
- Focus on healthy food, hydration, recovery, or sustainable habits.

Return only the tip.
"""

    client = _client()

    response = client.models.generate_content(
        model=settings.gemini_tip_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=300,
        ),
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")

    return text