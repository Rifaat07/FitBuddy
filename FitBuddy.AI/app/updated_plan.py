from google import genai
from google.genai import types

from .config import settings


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to the .env file before updating a plan."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def update_workout_plan(
    *,
    original_plan: str,
    feedback: str,
) -> str:

    prompt = f"""
You are FitBuddy.AI, an expert fitness coach.

Here is the user's existing workout plan:

--- EXISTING PLAN ---
{original_plan}
--- END EXISTING PLAN ---

Here is the user's feedback:

--- USER FEEDBACK ---
{feedback}
--- END USER FEEDBACK ---

Create an improved version of the workout plan based on the feedback.

Requirements:
- Preserve useful parts of the original plan.
- Make appropriate changes based on the feedback.
- Keep the plan practical and safe.
- Include exercises, sets, repetitions, rest periods, and recovery advice
  where appropriate.
- Use clear headings and bullet points.
- Do not diagnose medical conditions.
- If the feedback indicates an injury or medical issue, recommend consulting
  a qualified healthcare professional.

Return only the updated workout plan.
"""

    client = _client()

    response = client.models.generate_content(
        model=settings.gemini_workout_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=5000,
        ),
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError("Gemini returned an empty updated plan.")

    return text