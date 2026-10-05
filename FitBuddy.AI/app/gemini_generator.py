import time

from google import genai
from google.genai import types

from .config import settings


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to the .env file before generating an AI plan."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_workout_gemini(
    *,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy.AI, an expert fitness coach.

Create a personalized workout plan for the following user:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Workout Intensity: {intensity}

Requirements:
- Create a practical weekly workout plan.
- Include warm-up and cool-down.
- Include exercises, sets, repetitions, and rest periods.
- Adapt the plan to the user's goal and intensity.
- Keep the plan safe and beginner-friendly where appropriate.
- Include useful recovery advice.
- Use clear headings and bullet points.
- Do not diagnose medical conditions.
- If the user has a medical condition or injury, recommend consulting
  a qualified healthcare professional.

Return only the workout plan.
"""

    client = _client()

    max_attempts = 3
    delays = [5, 10, 20]

    last_error = None

    for attempt in range(max_attempts):
        try:
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
                raise RuntimeError("Gemini returned an empty workout plan.")

            return text

        except Exception as exc:
            last_error = exc

            error_text = str(exc)

            # Retry temporary Gemini server overloads.
            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt < max_attempts - 1:
                time.sleep(delays[attempt])

    raise RuntimeError(
        "Gemini is temporarily unavailable because the selected model "
        "is experiencing high demand. Please try generating the workout "
        "again in a few minutes."
    ) from last_error