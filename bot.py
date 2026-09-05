import os
import re
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from google import genai


# =========================================================
# 1. READ PROFILE + CONFIG
# =========================================================

profile = Path("profile.md").read_text(encoding="utf-8")
config = Path("config.md").read_text(encoding="utf-8")


# =========================================================
# 2. GEMINI SETUP
# =========================================================

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
- Create useful, practical and original graphic design content.
- Prefer topics that are genuinely useful for graphic designers.
- The content should feel written by an experienced human designer.

MY PROFILE:
{profile}

BOT CONFIGURATION:
{config}

TASK:
Choose ONE strong and relevant graphic design topic that would be valuable
for my LinkedIn audience.

Create:

1. POST TITLE / TOPIC
2. WHY THIS TOPIC
3. LINKEDIN POST
4. 5 RELEVANT HASHTAGS
5. IMAGE CONCEPT

The LinkedIn post should sound like a real professional graphic designer,
not like an AI or marketing agency.

Keep the final post clear, useful, practical and engaging.
Do not use unnecessary emojis.
"""


# =========================================================
# 3. GENERATE CONTENT
# =========================================================

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


content = response.text

print("\n========== GENERATED CONTENT ==========\n")
print(content)


# =========================================================
# 4. EXTRACT TOPIC + IMAGE CONCEPT
# =========================================================

def extract_section(text, section_number, next_section_number=None):
    if next_section_number:
        pattern = rf"{section_number}\.\s*.*?\n(.*?)(?=\n\s*{next_section_number}\.\s*)"
    else:
        pattern = rf"{section_number}\.\s*.*?\n(.*)$"

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        value = match.group(1).strip()
        value = re.sub(r"\*\*", "", value)
        return value.strip()

    return ""


topic = extract_section(content, 1, 2)
image_concept = extract_section(content, 5, None)


if not topic:
    topic = "Graphic Design Insight"

if not image_concept:
    image_concept = "A clean professional graphic design concept."


# =========================================================
# 5. FONT SETUP
# =========================================================

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def get_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)


# =========================================================
# 6. TEXT WRAPPING
# =========================================================

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word

        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# =========================================================
# 7. CREATE LINKEDIN IMAGE
# =========================================================

def create_linkedin_image(topic, image_concept):
    width = 1080
    height = 1350

    # Professional neutral background
    background = "#F5F3EE"
    dark = "#111111"
    accent = "#E85D3F"
    light_box = "#FFFFFF"
    muted = "#686868"

    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)

    # Fonts
    small_font = get_font(25)
    label_font = get_font(28, bold=True)
    title_font = get_font(70, bold=True)
    concept_font = get_font(32)
    footer_font = get_font(24)

    # -----------------------------------------------------
    # TOP LABEL
    # -----------------------------------------------------

    draw.text(
        (80, 75),
        "GRAPHIC DESIGN • DESIGN INSIGHT",
        font=label_font,
        fill=accent,
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title_lines = wrap_text(
        draw,
        topic,
        title_font,
        900,
    )

    y = 155

    for line in title_lines[:4]:
        draw.text(
            (80, y),
            line,
            font=title_font,
            fill=dark,
        )
        y += 85

    # -----------------------------------------------------
    # MAIN VISUAL CARD
    # -----------------------------------------------------

    card_top = max(y + 50, 480)
    card_bottom = 1040

    draw.rounded_rectangle(
        (70, card_top, 1010, card_bottom),
        radius=35,
        fill=light_box,
    )

    # Left accent block
    draw.rounded_rectangle(
        (105, card_top + 45, 440, card_bottom - 45),
        radius=25,
        fill=dark,
    )

    draw.text(
        (140, card_top + 90),
        "DESIGN",
        font=get_font(34, bold=True),
        fill=background,
    )

    draw.text(
        (140, card_top + 145),
        "PRINCIPLE",
        font=get_font(34, bold=True),
        fill=accent,
    )

    # Simple editorial lines
    line_y = card_top + 255

    for i, length in enumerate([235, 190, 220, 155]):
        draw.rounded_rectangle(
            (
                140,
                line_y + i * 55,
                140 + length,
                line_y + i * 55 + 12,
            ),
            radius=6,
            fill=background,
        )

    # -----------------------------------------------------
    # RIGHT CONCEPT
    # -----------------------------------------------------

    concept_x = 500
    concept_y = card_top + 70

    draw.text(
        (concept_x, concept_y),
        "KEY IDEA",
        font=get_font(26, bold=True),
        fill=accent,
    )

    concept_lines = wrap_text(
        draw,
        image_concept,
        concept_font,
        440,
    )

    concept_y += 65

    for line in concept_lines[:8]:
        draw.text(
            (concept_x, concept_y),
            line,
            font=concept_font,
            fill=dark,
        )
        concept_y += 45

    # -----------------------------------------------------
    # SMALL VISUAL ELEMENTS
    # -----------------------------------------------------

    circle_x = 850
    circle_y = card_bottom - 120

    draw.ellipse(
        (
            circle_x - 45,
            circle_y - 45,
            circle_x + 45,
            circle_y + 45,
        ),
        fill=accent,
    )

    draw.rectangle(
        (
            circle_x - 15,
            circle_y - 15,
            circle_x + 15,
            circle_y + 15,
        ),
        fill=background,
    )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    draw.text(
        (80, 1130),
        "CLARITY • HIERARCHY • PURPOSE",
        font=label_font,
        fill=dark,
    )

    draw.text(
        (80, 1195),
        "A practical design perspective for better visual communication.",
        font=small_font,
        fill=muted,
    )

    draw.text(
        (80, 1270),
        "LinkedIn Design Insight",
        font=footer_font,
        fill=muted,
    )

    output_file = "linkedin_image.png"
    image.save(output_file, "PNG", optimize=True)

    return output_file


# =========================================================
# 8. GENERATE IMAGE
# =========================================================

image_file = create_linkedin_image(
    topic,
    image_concept,
)

print(f"\nImage created: {image_file}")


# =========================================================
# 9. TELEGRAM SETUP
# =========================================================

telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]

telegram_base = f"https://api.telegram.org/bot{telegram_token}"


# =========================================================
# 10. SEND IMAGE TO TELEGRAM
# =========================================================

with open(image_file, "rb") as photo:
    photo_result = requests.post(
        f"{telegram_base}/sendPhoto",
        data={
            "chat_id": telegram_chat_id,
            "caption": "🖼️ LinkedIn image ready",
        },
        files={
            "photo": photo,
        },
        timeout=60,
    )

photo_result.raise_for_status()

print("Successfully sent image to Telegram.")


# =========================================================
# 11. SEND FULL LINKEDIN CONTENT
# =========================================================

message = f"""🤖 LinkedIn Content Ready

{content}
"""


# Telegram messages have a size limit, so split if necessary.
max_length = 4000

chunks = [
    message[i:i + max_length]
    for i in range(0, len(message), max_length)
]


for chunk in chunks:
    result = requests.post(
        f"{telegram_base}/sendMessage",
        data={
            "chat_id": telegram_chat_id,
            "text": chunk,
        },
        timeout=30,
    )

    result.raise_for_status()


print("Successfully sent LinkedIn content to Telegram.")
print("DONE.")
