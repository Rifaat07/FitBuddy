from google import genai
from app.config import settings

print("===================================")
print("FitBuddy Gemini Connection Test")
print("===================================")

print("API key loaded:", bool(settings.gemini_api_key))
print("Workout model:", settings.gemini_workout_model)
print("Tip model:", settings.gemini_tip_model)

if not settings.gemini_api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not loaded. "
        "Check your .env file."
    )

print("\nConnecting to Gemini...")

client = genai.Client(
    api_key=settings.gemini_api_key
)

response = client.models.generate_content(
    model=settings.gemini_tip_model,
    contents="Give me one short healthy fitness tip."
)

print("\n===================================")
print("Gemini Response")
print("===================================")

print(response.text)

print("\nGemini connection test PASSED!")