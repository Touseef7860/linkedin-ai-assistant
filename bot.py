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
Research current/relevant graphic design topics using Google Search.
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

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    ),
)

print(response.text)
