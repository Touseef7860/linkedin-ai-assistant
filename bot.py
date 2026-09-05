import os
import re
import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from google import genai


# =========================================================
# FILES
# =========================================================

profile = Path("profile.md").read_text(encoding="utf-8")
config = Path("config.md").read_text(encoding="utf-8")


# =========================================================
# GEMINI
# =========================================================

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
You are a professional graphic designer's personal LinkedIn content assistant.

PROFILE:
{profile}

CONFIGURATION:
{config}

IMPORTANT:
- Personal LinkedIn profile.
- Professional Graphic Designer.
- Never invent clients, awards, projects, qualifications or results.
- Never mention Red Line Arts unless explicitly requested.
- Write natural professional English.
- No generic motivational content.
- No clickbait.
- No fake personal stories.
- Focus on practical graphic design knowledge.
- The content should feel written by an experienced designer.

TASK:
Choose ONE highly useful graphic design topic for today's LinkedIn post.

Return EXACTLY these sections:

TITLE:
A short strong title, maximum 12 words.

WHY:
One short paragraph explaining why the topic matters.

POST:
A polished LinkedIn post, around 150-250 words.

HASHTAGS:
Exactly 5 relevant hashtags.

IMAGE:
Give a short visual direction for a professional LinkedIn graphic.
Maximum 40 words.

The visual should be educational/editorial, not a generic AI illustration.
"""


# =========================================================
# GENERATE CONTENT WITH FALLBACK MODELS
# =========================================================

models = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

response = None

for model in models:
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        print(f"Gemini model used: {model}")
        break
    except Exception as e:
        print(f"{model} failed: {e}")


if response is None:
    raise RuntimeError("All Gemini models failed.")


content = response.text.strip()

print("\n========== CONTENT ==========\n")
print(content)


# =========================================================
# SECTION EXTRACTOR
# =========================================================

def extract_section(name, text):
    pattern = rf"{name}\s*:\s*(.*?)(?=\n(?:TITLE|WHY|POST|HASHTAGS|IMAGE)\s*:|\Z)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    return ""


title = extract_section("TITLE", content)
why = extract_section("WHY", content)
post = extract_section("POST", content)
hashtags = extract_section("HASHTAGS", content)
image_direction = extract_section("IMAGE", content)

if not title:
    title = "A Better Way to Think About Design"

if not image_direction:
    image_direction = "A clean editorial graphic explaining the main design principle."


# =========================================================
# IMAGE HELPERS
# =========================================================

WIDTH = 1080
HEIGHT = 1350

BG = "#F4F1EA"
BLACK = "#111111"
WHITE = "#FFFFFF"
GREY = "#77736D"
LIGHT_GREY = "#DDD8CF"
ACCENT = "#E4573D"
BLUE = "#315CFF"


FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)


def text_width(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word

        if text_width(draw, test, f) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def draw_header(draw, label):
    draw.text(
        (70, 55),
        "DESIGN NOTE",
        font=font(25, True),
        fill=ACCENT,
    )

    draw.text(
        (WIDTH - 310, 58),
        label.upper(),
        font=font(20),
        fill=GREY,
    )

    draw.line(
        (70, 105, WIDTH - 70, 105),
        fill=LIGHT_GREY,
        width=2,
    )


# =========================================================
# LAYOUT 1 — EDITORIAL
# =========================================================

def layout_editorial(img, draw):
    draw_header(draw, "Graphic Design")

    title_font = font(72, True)

    lines = wrap(draw, title, title_font, 900)

    y = 155

    for line in lines[:4]:
        draw.text(
            (70, y),
            line,
            font=title_font,
            fill=BLACK,
        )
        y += 86

    # Editorial visual
    card_top = 520

    rounded(
        draw,
        (70, card_top, 1010, 1035),
        35,
        WHITE,
    )

    draw.text(
        (110, card_top + 45),
        "THE PRINCIPLE",
        font=font(23, True),
        fill=ACCENT,
    )

    concept_lines = wrap(
        draw,
        image_direction,
        font(34, True),
        820,
    )

    cy = card_top + 105

    for line in concept_lines[:7]:
        draw.text(
            (110, cy),
            line,
            font=font(34, True),
            fill=BLACK,
        )
        cy += 48

    # Abstract typography
    draw.text(
        (110, 820),
        "Aa",
        font=font(150, True),
        fill=BLACK,
    )

    draw.text(
        (275, 850),
        "TYPE",
        font=font(35, True),
        fill=ACCENT,
    )

    draw.line(
        (110, 985, 930, 985),
        fill=BLACK,
        width=5,
    )

    draw.text(
        (70, 1140),
        "CLARITY  /  HIERARCHY  /  PURPOSE",
        font=font(25, True),
        fill=BLACK,
    )


# =========================================================
# LAYOUT 2 — BEFORE / AFTER
# =========================================================

def layout_before_after(img, draw):
    draw_header(draw, "Before / After")

    draw.text(
        (70, 150),
        title,
        font=font(62, True),
        fill=BLACK,
    )

    # BEFORE
    rounded(
        draw,
        (70, 290, 505, 920),
        30,
        WHITE,
    )

    draw.text(
        (105, 330),
        "BEFORE",
        font=font(25, True),
        fill=ACCENT,
    )

    # cluttered visual
    sizes = [42, 30, 55, 28, 45, 34]

    y = 430

    for i, size in enumerate(sizes):
        txt = ["Aa", "TYPE", "BRAND", "DESIGN", "IDEA", "VISUAL"][i]

        draw.text(
            (105 + (i % 2) * 100, y),
            txt,
            font=font(size, True),
            fill=BLACK,
        )

        y += 70

    draw.text(
        (105, 850),
        "Too much competing",
        font=font(24),
        fill=GREY,
    )

    # AFTER
    rounded(
        draw,
        (575, 290, 1010, 920),
        30,
        BLACK,
    )

    draw.text(
        (610, 330),
        "AFTER",
        font=font(25, True),
        fill=ACCENT,
    )

    draw.text(
        (610, 470),
        "Aa",
        font=font(120, True),
        fill=WHITE,
    )

    draw.text(
        (610, 650),
        "Clear",
        font=font(55, True),
        fill=WHITE,
    )

    draw.text(
        (610, 720),
        "Hierarchy",
        font=font(55, True),
        fill=ACCENT,
    )

    draw.text(
        (610, 850),
        "One clear visual priority",
        font=font(24),
        fill=LIGHT_GREY,
    )

    draw.text(
        (70, 1010),
        "GOOD DESIGN REDUCES VISUAL NOISE.",
        font=font(34, True),
        fill=BLACK,
    )

    draw.text(
        (70, 1080),
        "The goal is not to add more. It's to communicate better.",
        font=font(27),
        fill=GREY,
    )


# =========================================================
# LAYOUT 3 — CHECKLIST
# =========================================================

def layout_checklist(img, draw):
    draw_header(draw, "Design Checklist")

    title_font = font(65, True)

    lines = wrap(draw, title, title_font, 900)

    y = 150

    for line in lines[:3]:
        draw.text(
            (70, y),
            line,
            font=title_font,
            fill=BLACK,
        )
        y += 78

    items = [
        "Clear visual hierarchy",
        "Consistent spacing",
        "Controlled typography",
        "Strong contrast",
        "One clear message",
    ]

    start_y = 480

    for i, item in enumerate(items, 1):
        yy = start_y + (i - 1) * 125

        draw.ellipse(
            (75, yy, 125, yy + 50),
            fill=ACCENT,
        )

        draw.text(
            (91, yy + 5),
            str(i),
            font=font(24, True),
            fill=WHITE,
        )

        draw.text(
            (155, yy - 2),
            item,
            font=font(34, True),
            fill=BLACK,
        )

        draw.line(
            (155, yy + 55, 960, yy + 55),
            fill=LIGHT_GREY,
            width=2,
        )

    draw.text(
        (70, 1120),
        "SAVE THIS FOR YOUR NEXT DESIGN PROJECT.",
        font=font(27, True),
        fill=ACCENT,
    )


# =========================================================
# LAYOUT 4 — PROCESS
# =========================================================

def layout_process(img, draw):
    draw_header(draw, "Design Process")

    draw.text(
        (70, 150),
        title,
        font=font(64, True),
        fill=BLACK,
    )

    steps = [
        ("01", "DEFINE", "Understand the goal"),
        ("02", "STRUCTURE", "Build the hierarchy"),
        ("03", "DESIGN", "Create the visual system"),
        ("04", "REFINE", "Remove what is unnecessary"),
    ]

    y = 390

    for number, heading, description in steps:
        draw.text(
            (70, y),
            number,
            font=font(50, True),
            fill=ACCENT,
        )

        draw.text(
            (190, y),
            heading,
            font=font(34, True),
            fill=BLACK,
        )

        draw.text(
            (190, y + 50),
            description,
            font=font(26),
            fill=GREY,
        )

        draw.line(
            (190, y + 100, 970, y + 100),
            fill=LIGHT_GREY,
            width=2,
        )

        y += 185

    draw.text(
        (70, 1150),
        "DESIGN IS A PROCESS OF MAKING DECISIONS.",
        font=font(29, True),
        fill=BLACK,
    )


# =========================================================
# LAYOUT 5 — BIG STATEMENT
# =========================================================

def layout_statement(img, draw):
    draw_header(draw, "Design Principle")

    # large accent circle
    draw.ellipse(
        (710, 190, 960, 440),
        fill=ACCENT,
    )

    draw.text(
        (775, 245),
        "01",
        font=font(70, True),
        fill=WHITE,
    )

    title_font = font(75, True)

    lines = wrap(
        draw,
        title,
        title_font,
        850,
    )

    y = 220

    for line in lines[:5]:
        draw.text(
            (70, y),
            line,
            font=title_font,
            fill=BLACK,
        )
        y += 90

    rounded(
        draw,
        (70, 760, 1010, 1030),
        30,
        BLACK,
    )

    concept_lines = wrap(
        draw,
        image_direction,
        font(32),
        820,
    )

    y = 825

    for line in concept_lines[:5]:
        draw.text(
            (110, y),
            line,
            font=font(32),
            fill=WHITE,
        )
        y += 48

    draw.text(
        (70, 1130),
        "A DESIGNER'S JOB IS TO MAKE THE MESSAGE CLEAR.",
        font=font(27, True),
        fill=ACCENT,
    )


# =========================================================
# SMART LAYOUT SELECTION
# =========================================================

def choose_layout():
    text = (
        title + " " +
        image_direction + " " +
        post
    ).lower()

    if any(word in text for word in [
        "before",
        "after",
        "mistake",
        "wrong",
        "improve",
        "weak",
        "better",
        "bad design",
    ]):
        return "before_after"

    if any(word in text for word in [
        "steps",
        "process",
        "workflow",
        "how to",
        "approach",
        "method",
    ]):
        return "process"

    if any(word in text for word in [
        "checklist",
        "mistakes",
        "rules",
        "tips",
        "principles",
        "things",
    ]):
        return "checklist"

    if any(word in text for word in [
        "type",
        "font",
        "typography",
        "logo",
        "branding",
        "identity",
    ]):
        return "editorial"

    return "statement"


# =========================================================
# CREATE IMAGE
# =========================================================

def create_image():
    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BG,
    )

    draw = ImageDraw.Draw(img)

    layout = choose_layout()

    print(f"Selected visual layout: {layout}")

    if layout == "before_after":
        layout_before_after(img, draw)

    elif layout == "checklist":
        layout_checklist(img, draw)

    elif layout == "process":
        layout_process(img, draw)

    elif layout == "editorial":
        layout_editorial(img, draw)

    else:
        layout_statement(img, draw)

    # Small brand-free footer
    draw.text(
        (WIDTH - 270, HEIGHT - 55),
        "DESIGN INSIGHT",
        font=font(18, True),
        fill=GREY,
    )

    filename = "linkedin_image.png"

    img.save(
        filename,
        "PNG",
        optimize=True,
    )

    return filename


# =========================================================
# GENERATE IMAGE
# =========================================================

image_file = create_image()

print(f"Image generated: {image_file}")


# =========================================================
# TELEGRAM
# =========================================================

telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]

telegram_base = (
    f"https://api.telegram.org/bot{telegram_token}"
)


# =========================================================
# SEND IMAGE
# =========================================================

with open(image_file, "rb") as photo:
    result = requests.post(
        f"{telegram_base}/sendPhoto",
        data={
            "chat_id": telegram_chat_id,
            "caption": "🖼️ PRO LinkedIn visual ready",
        },
        files={
            "photo": photo,
        },
        timeout=60,
    )

result.raise_for_status()

print("Image sent to Telegram.")


# =========================================================
# SEND CAPTION
# =========================================================

telegram_message = f"""🤖 LINKEDIN CONTENT READY

TITLE:
{title}

WHY:
{why}

POST:
{post}

HASHTAGS:
{hashtags}

IMAGE CONCEPT:
{image_direction}
"""


# Telegram safe chunks
chunks = [
    telegram_message[i:i + 4000]
    for i in range(0, len(telegram_message), 4000)
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


print("LinkedIn caption sent to Telegram.")
print("========== DONE ==========")
