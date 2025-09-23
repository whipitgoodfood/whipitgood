import os, re, sys, json, random
from datetime import datetime
from pathlib import Path

# Optional: use Pillow to make a simple placeholder image for each post
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except:
    PIL_OK = False

# ----------- Config ----------
SITE_CATEGORY_POOL = [
    ("creami", "Ninja Creami"),
    ("frozen-treats", "Frozen Treats"),
    ("protein-bakes", "Protein Bakes"),
    ("seasonal", "Seasonal"),
]
ASSETS_DIR = Path("assets/images")
POSTS_DIR = Path("_posts")
MODEL = "gpt-4o-mini"  # small + cheap; change if you prefer
# -----------------------------

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s[:60] or "recipe"

def prompt(category_slug, category_label):
    return f"""
You are writing a single high-protein dessert or frozen treat recipe for a blog called "Whip It Good".
Output ONLY a valid Markdown post with Jekyll YAML front matter followed by one short intro paragraph. Nothing else.

Rules:
- layout must be "recipe"
- categories must be exactly: {category_slug}
- image must be a relative path under /assets/images/ using a simple slugged filename (e.g., /assets/images/choc-protein-ice-cream.jpg)
- times must be ISO 8601 duration strings (e.g., PT5M)
- nutrition fields must be strings with units where relevant (e.g., "25 g")
- keep ingredients to 6–10 lines, instructions to 4–8 steps

YAML front matter fields (exact keys):
layout: recipe
title: ...
subtitle: ...
description: ...
image: /assets/images/....jpg
image_alt: ...
categories: {category_slug}
tags: [high-protein, dessert, {category_slug}]
prep_time: "PT#M"
prep_time_human: "..."
cook_time: "PT#M"
cook_time_human: "..."
total_time: "PT#M"
total_time_human: "..."
recipe_yield: "..."
ingredients:
  - ...
instructions:
  - ...
nutrition:
  calories: "..."
  protein: "..."
  carbs: "..."
  fat: "..."

Recipe topic: {category_label}. Keep it practical, macro-friendly, and tasty. Avoid brand names. Reasonable sweeteners and protein choices.
"""

def call_openai(prompt_text):
    # OpenAI Python SDK v1 style
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a careful recipe writer. Follow format exactly."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content

def extract_front_matter(md: str):
    # expects ---\nYAML\n---\n body
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", md, re.S)
    if not m:
        raise ValueError("Model output missing valid Jekyll front matter.")
    return m.group(1), m.group(2)

def pick_category():
    return random.choice(SITE_CATEGORY_POOL)

def ensure_dirs():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

def make_placeholder_image(text, dest_path):
    if not PIL_OK:
        return
    img = Image.new("RGB", (1200, 800), color=(248, 248, 248))
    d = ImageDraw.Draw(img)
    try:
        # System fonts vary on Actions; draw with default font
        pass
    except:
        pass
    # simple centered text block
    title = (text[:38] + "…") if len(text) > 40 else text
    d.text((40, 40), f"Whip It Good\n{title}", fill=(20, 20, 20))
    img.save(dest_path, "JPEG", quality=82, optimize=True)

def main():
    ensure_dirs()
    cat_slug, cat_label = pick_category()
    out_md = call_openai(prompt(cat_slug, cat_label)).strip()

    yml, body = extract_front_matter(out_md)

    # Pull title and image path from YAML with a light regex (we keep it simple)
    title_m = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", yml, re.M)
    image_m = re.search(r"^image:\s*(/assets/images/.*)\s*$", yml, re.M)
    if not title_m or not image_m:
        raise ValueError("Missing title or image in YAML.")

    title = title_m.group(1).strip()
    image_rel = image_m.group(1).strip()
    slug = slugify(title)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    post_path = POSTS_DIR / f"{today}-{slug}.md"

    # If that filename already exists, add a suffix
    i = 2
    base_post = post_path
    while post_path.exists():
        post_path = POSTS_DIR / f"{today}-{slug}-{i}.md"
        i += 1

    # Make a placeholder image if one is missing
    img_path = Path(image_rel.lstrip("/"))
    if not img_path.parent.exists():
        img_path.parent.mkdir(parents=True, exist_ok=True)
    if not img_path.exists() and PIL_OK:
        make_placeholder_image(title, img_path)

    # Write final file
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(f"---\n{yml}\n---\n{body.strip()}\n")

    print(f"Created post: {post_path}")
    print(f"Image path:   {img_path} {'(created placeholder)' if img_path.exists() else ''}")

if __name__ == "__main__":
    if "OPENAI_API_KEY" not in os.environ:
        print("OPENAI_API_KEY is not set")
        sys.exit(1)
    main()
