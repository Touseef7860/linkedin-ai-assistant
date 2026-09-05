import os
from pathlib import Path
from google import genai
from google.genai import types

# Load your personal LinkedIn profile and bot configuration
profile = Path("profile.md").read_text(encoding="utf-8")
config = Path("config.md").read_text(encoding="utf-8")

# Gemini API key comes securely from GitHub Secrets
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
You are my personal LinkedIn content assistant.

IMPORTANT:
- This is a PERSONAL LinkedIn profile, not a company page.
- The person is a professional Graphic Designer.
- Never mention or promote Red Line Arts unless explicitly requested.
- Never invent clients, awards, qualifications, projects, results or experience.
- Write in natural professional English.
- Avoid generic motivational content and clickbait.
- Create useful, practical, original design content.
- Prefer topics that are currently relevant to graphic designers.

MY PROFILE:
{profile}

BOT CONFIGURATION:
{config}

TASK:
Choose ONE strong and relevant graphic design topic that would be valuable for my LinkedIn audience.
Choose ONE strong topic that would be valuable for my LinkedIn audience.

Then create:

1. POST TITLE / TOPIC
2. WHY THIS TOPIC
3. LINKEDIN POST
4. 5 RELEVANT HASHTAGS
5. IMAGE CONCEPT

The LinkedIn post should sound like a real professional graphic designer,
not like an AI or marketing agency.

Keep the final post clear, useful and engaging without unnecessary emojis.
"""

models_to_try = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

response = None

for model_name in models_to_try:
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        print(f"Successfully used: {model_name}")
        break
    except Exception as e:
        print(f"{model_name} failed: {e}")

if response is None:
    raise RuntimeError("All Gemini models failed. Please try again later.")

print(response.text)
