import os, re, random, textwrap, json
from datetime import datetime
from pathlib import Path

import yaml  # PyYAML
try:
    from PIL import Image, ImageDraw
    PIL_OK = True
except Exception:
    PIL_OK = False

try:
    import requests
    REQ_OK = True
except Exception:
    REQ_OK = False

# ------------- Settings -------------
POSTS_DIR = Path("_posts")
IMG_HERO_DIR = Path("assets/images")
IMG_OG_DIR = Path("assets/og")
IMG_PIN_DIR = Path("assets/pins")
IMG_SRC_DIR = Path("assets/src")  # original downloads

CATEGORIES = ["creami", "frozen-treats", "protein-bakes", "seasonal"]
SITE_NAME = "Whip It Good"
TEXT = (20, 20, 20)
BG_LIGHT = (248, 248, 248)
OG_BG = (242, 246, 255)
PIN_BG = (255, 248, 242)
# ------------------------------------

SPINTAX_SUBTITLES = [
    "Macro-friendly {treat} that actually tastes good",
    "Light, {creamy|fudgy|frosty} and protein-packed",
    "{Easy|Simple} to make, {big|serious} on flavor",
]
SPINTAX_DESCS = [
    "A {high-protein|macro-friendly} {treat} you can make with simple pantry staples.",
    "This {treat} keeps calories in check and texture {creamy|satisfying}.",
]
FLAVORS = {
    "creami": [
        ("Double Chocolate Protein Ice Cream", [
            "1 cup unsweetened almond milk",
            "1/2 cup nonfat Greek yogurt",
            "1 scoop chocolate whey or casein",
            "1 tbsp cocoa powder",
            "1–2 tsp allulose or preferred sweetener",
            "Pinch of salt",
        ]),
        ("Vanilla Bean Protein Ice Cream", [
            "1 cup unsweetened almond milk",
            "1/2 cup nonfat Greek yogurt",
            "1 scoop vanilla whey or casein",
            "1/2 tsp vanilla extract",
            "1–2 tsp allulose or preferred sweetener",
            "Pinch of salt",
        ]),
    ],
    "frozen-treats": [
        ("Triple Berry Protein Pops", [
            "1 cup nonfat Greek yogurt",
            "3/4 cup mixed berries (frozen ok)",
            "1/2 cup unsweetened almond milk",
            "1 scoop vanilla whey protein",
            "1–2 tsp allulose or preferred sweetener",
            "1 tsp lemon juice",
        ]),
        ("Peaches & Cream Protein Pops", [
            "1 cup nonfat Greek yogurt",
            "1 cup diced peaches (frozen ok)",
            "1/2 cup unsweetened almond milk",
            "1 scoop vanilla whey",
            "1–2 tsp allulose",
            "Pinch of salt",
        ]),
    ],
    "protein-bakes": [
        ("One-Bowl Protein Brownies", [
            "1/2 cup chocolate whey/casein blend",
            "1/4 cup cocoa powder",
            "1/4 cup oat flour",
            "1/4 cup unsweetened applesauce",
            "1/4 cup nonfat Greek yogurt",
            "2 tbsp allulose or sweetener",
            "1 egg",
            "1/4 tsp baking powder",
            "Pinch of salt",
        ]),
    ],
    "seasonal": [
        ("Pumpkin Pie Protein Soft Serve", [
            "1 cup unsweetened almond milk",
            "1/2 cup pumpkin purée",
            "1 scoop vanilla casein or blend",
            "1–2 tsp allulose",
            "1/2 tsp pumpkin pie spice",
            "Pinch of salt",
        ]),
    ],
}
INSTRUCTIONS = {
    "creami": [
        "Blend all ingredients until completely smooth.",
        "Pour into a Ninja Creami pint and freeze 12–24 hours.",
        "Spin on Lite Ice Cream. Re-spin as needed for creaminess.",
        "If crumbly, add 1–2 tbsp almond milk and re-spin.",
    ],
    "frozen-treats": [
        "Blend all ingredients until smooth.",
        "Pour into popsicle molds.",
        "Freeze at least 4 hours or until solid.",
        "Run molds under warm water 10–15 seconds to release.",
    ],
    "protein-bakes": [
        "Heat oven to 350°F (175°C). Line or grease your pan.",
        "Whisk dry ingredients, then add wet and stir to combine.",
        "If needed, add 1–3 tbsp water to reach a thick batter.",
        "Bake until set; cool before slicing.",
    ],
    "seasonal": [
        "Blend everything until smooth.",
        "Churn in Creami or freeze 2–3 hours, stirring every 30–45 minutes.",
        "Serve soft-serve style and enjoy.",
    ],
}
TIPS = [
    "For extra creaminess, add 1 tbsp sugar-free pudding mix.",
    "Casein or blend proteins make thicker, less icy results.",
    "Allulose stays softer than erythritol in frozen treats.",
]
FAQ_BANK = [
    ("Can I use whey isolate?", "Yes, but the texture may be icier. A whey-casein blend or adding 1–2 tbsp Greek yogurt helps."),
    ("How do I sweeten without aftertaste?", "Try allulose or a blend of allulose + a few drops of liquid stevia."),
    ("Can I make it dairy-free?", "Use a plant protein you like and swap Greek yogurt for coconut yogurt or silken tofu."),
]
TROUBLESHOOT = {
    "creami": [
        ("Crumbly after first spin", "Add 1–2 tbsp milk and re-spin. Casein/blend proteins help bind water."),
        ("Icy texture", "Use allulose, add a spoon of yogurt or pudding mix, and avoid over-freezing pints for days."),
    ],
    "frozen-treats": [
        ("Won’t release from molds", "Run the mold under warm water 10–15 seconds, then twist gently."),
        ("Too icy", "Blend longer to fully dissolve protein and sweetener; use allulose for softer bite."),
    ],
}

def spin(s: str) -> str:
    def repl(m): return random.choice(m.group(1).split("|"))
    return re.sub(r"\{([^{}]+)\}", repl, s)

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s[:70] or "recipe"

def ensure_dirs():
    for p in (POSTS_DIR, IMG_HERO_DIR, IMG_OG_DIR, IMG_PIN_DIR, IMG_SRC_DIR):
        p.mkdir(parents=True, exist_ok=True)

def macro_estimate(cat: str):
    if cat == "creami":           return ("160 kcal", "25 g", "8 g", "3 g")
    if cat == "frozen-treats":    return ("90 kcal", "10 g", "11 g", "1 g")
    if cat == "protein-bakes":    return ("150 kcal", "12 g", "16 g", "4 g")
    return ("160 kcal", "22 g", "14 g", "3 g")

# ---------- Image helpers ----------
def cover_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    # Resize to fill target, cropping excess (like CSS object-fit: cover)
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    tgt_ratio = target_w / target_h
    if src_ratio > tgt_ratio:
        # source wider than target: height matches, crop width
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img2 = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img2.crop((left, top, left + target_w, top + target_h))

def draw_card_bg(w, h, bg):
    if not PIL_OK: return None
    return Image.new("RGB", (w, h), color=bg)

def title_overlay(base: Image.Image, title: str, subtitle: str | None):
    if not PIL_OK: return base
    d = ImageDraw.Draw(base)
    # Simple text block
    pad = 36
    y = pad
    d.rectangle([pad-10, pad-10, base.width - pad, y + 120], fill=(255,255,255,180))
    d.text((pad, y), SITE_NAME, fill=TEXT); y += 48
    wrapped = textwrap.fill(title, width=28)
    d.text((pad, y), wrapped, fill=TEXT); y += 28 * (1 + wrapped.count("\n"))
    if subtitle:
        d.text((pad, y+8), textwrap.fill(subtitle, 32), fill=(60,60,60))
    return base

def pexels_search_and_download(query: str, dest_src_path: Path):
    """Returns (True/False, credit_name, credit_url, provider)"""
    if not (REQ_OK and os.getenv("PEXELS_API_KEY")):
        return False, None, None, None
    headers = {"Authorization": os.environ["PEXELS_API_KEY"]}
    url = "https://api.pexels.com/v1/search"
    # bias toward food/ice cream/popsicles
    q = f"{query} food dessert ice cream popsicle smoothie yogurt"
    params = {"query": q, "per_page": 1, "orientation": "landscape"}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    if r.status_code != 200:
        return False, None, None, None
    data = r.json()
    if not data.get("photos"):
        return False, None, None, None
    p = data["photos"][0]
    src = p.get("src", {})
    image_url = src.get("original") or src.get("large2x") or src.get("large")
    if not image_url:
        return False, None, None, None
    img_bytes = requests.get(image_url, timeout=30).content
    dest_src_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_src_path, "wb") as f:
        f.write(img_bytes)
    credit_name = p.get("photographer")
    credit_url = p.get("url")
    return True, credit_name, credit_url, "Pexels"

def make_images_from_src(src_path: Path, slug: str, title: str, subtitle: str):
    hero = IMG_HERO_DIR / f"{slug}.jpg"
    og = IMG_OG_DIR / f"{slug}-og.jpg"
    pin = IMG_PIN_DIR / f"{slug}-pin.jpg"
    if PIL_OK and src_path.exists():
        img = Image.open(src_path).convert("RGB")
        # Hero 1200x800
        h = cover_resize(img, 1200, 800)
        h.save(hero, "JPEG", quality=86, optimize=True)
        # OG 1200x630 with subtle overlay
        o = cover_resize(img, 1200, 630)
        title_overlay(o, title, subtitle).save(og, "JPEG", quality=86, optimize=True)
        # Pin 1200x1800 with overlay
        p = cover_resize(img, 1200, 1800)
        title_overlay(p, title, subtitle).save(pin, "JPEG", quality=86, optimize=True)
    return hero, og, pin

# ---------- Content blocks ----------
def build_sections(cat, title):
    tips = random.sample(TIPS, k=min(3, len(TIPS)))
    variations = [
        "Swap whey for a whey/casein blend to improve texture.",
        "Use allulose for softer freeze; erythritol sets harder.",
        "Add 1–2 tbsp nonfat Greek yogurt for creaminess.",
        "Stir in mix-ins after the first spin (chips, berries, cookie crumbles).",
    ]
    ts_list = TROUBLESHOOT.get(cat, [])
    faqs = random.sample(FAQ_BANK, k=min(2, len(FAQ_BANK)))

    md = []
    md.append("## Tips")
    for t in tips: md.append(f"- {t}")
    md.append("\n## Variations")
    for v in variations: md.append(f"- {v}")
    if ts_list:
        md.append("\n## Troubleshooting")
        for h, s in ts_list:
            md.append(f"**{h}.** {s}")
    md.append("\n## FAQs")
    for q, a in faqs:
        md.append(f"**{q}**\n\n{a}")
    md.append("\n## More to explore")
    links = {
        "creami": "{{ '/category/creami/' | relative_url }}",
        "frozen-treats": "{{ '/category/frozen-treats/' | relative_url }}",
        "protein-bakes": "{{ '/category/protein-bakes/' | relative_url }}",
        "seasonal": "{{ '/category/seasonal/' | relative_url }}",
    }
    md.append(f"- More in this category: {links[cat]}")
    md.append("- Start here: {{ '/' | relative_url }}")
    return "\n".join(md)

def spin_text(s: str, treat_word: str) -> str:
    return spin(s).replace("{treat}", treat_word)

def main():
    ensure_dirs()

    cat = random.choice(CATEGORIES)
    title, ingredients = random.choice(FLAVORS[cat])
    treat_word = "treat" if cat != "protein-bakes" else "bake"
    subtitle = spin_text(random.choice(SPINTAX_SUBTITLES), treat_word)
    description = spin_text(random.choice(SPINTAX_DESCS), treat_word)
    steps = INSTRUCTIONS[cat]
    calories, protein, carbs, fat = macro_estimate(cat)

    slug = slugify(title)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    post_path = POSTS_DIR / f"{today}-{slug}.md"
    i = 2
    while post_path.exists():
        post_path = POSTS_DIR / f"{today}-{slug}-{i}.md"
        i += 1

    # Try to fetch a real photo from Pexels
    credit_name = credit_url = credit_provider = None
    src_path = IMG_SRC_DIR / f"{slug}-src.jpg"
    got_remote = False
    if REQ_OK and os.getenv("PEXELS_API_KEY"):
        q = re.sub(r"\bprotein\b", "", title, flags=re.I).strip()
        ok, credit_name, credit_url, credit_provider = pexels_search_and_download(q, src_path)
        got_remote = ok

    # Build images from either the remote source or a branded filler
    if got_remote and PIL_OK:
        hero_path, og_path, pin_path = make_images_from_src(src_path, slug, title, subtitle)
    else:
        # fallback: branded cards
        hero_path = IMG_HERO_DIR / f"{slug}.jpg"
        og_path = IMG_OG_DIR / f"{slug}-og.jpg"
        pin_path = IMG_PIN_DIR / f"{slug}-pin.jpg"
        if PIL_OK:
            for w, h, bg, out in [(1200,800,BG_LIGHT,hero_path),(1200,630,OG_BG,og_path),(1200,1800,PIN_BG,pin_path)]:
                img = Image.new("RGB", (w,h), color=bg)
                title_overlay(img, title, subtitle).save(out, "JPEG", quality=86, optimize=True)

    hero_rel = f"/{hero_path.as_posix()}"
    og_rel = f"/{og_path.as_posix()}"
    pin_rel = f"/{pin_path.as_posix()}"

    # Times / yield
    if cat == "protein-bakes":
        prep, cook, total = ("PT10M","PT15M","PT25M")
        prep_h, cook_h, total_h = ("10 minutes","15 minutes","25 minutes")
        recipe_yield = "9 squares"
    elif cat == "frozen-treats":
        prep, cook, total = ("PT5M","PT0M","PT5M")
        prep_h, cook_h, total_h = ("5 minutes","0 minutes","5 minutes")
        recipe_yield = "6 pops"
    else:
        prep, cook, total = ("PT5M","PT0M","PT5M")
        prep_h, cook_h, total_h = ("5 minutes","0 minutes","5 minutes")
        recipe_yield = "1 pint" if cat == "creami" else "2 servings"

    # Front matter
    front = {
        "layout": "recipe",
        "title": title,
        "subtitle": subtitle,
        "description": description,
        "image": og_rel,       # social image (OG)
        "hero_image": hero_rel, # on-page hero
        "pin_image": pin_rel,
        "pin_title": f"{title} | {SITE_NAME}",
        "pin_description": f"{description} (Protein: {protein}, Calories: {calories})",
        "image_alt": title,
        "categories": cat,
        "tags": ["high-protein", "dessert", cat],
        "prep_time": prep,
        "prep_time_human": prep_h,
        "cook_time": cook,
        "cook_time_human": cook_h,
        "total_time": total,
        "total_time_human": total_h,
        "recipe_yield": recipe_yield,
        "ingredients": ingredients,
        "instructions": steps,
        "nutrition": {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
        },
    }

    if credit_name and credit_url:
        front["credit_name"] = credit_name
        front["credit_url"] = credit_url
        front["credit_provider"] = credit_provider

    body = "Short, practical, and macro-friendly. Save this base and remix flavors next time.\n\n"
    body += build_sections(cat, title)

    yaml_front = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(f"---\n{yaml_front}---\n{body}\n")

    print(f"Created post: {post_path}")
    print(f"Hero image:   {hero_path} ({'ok' if hero_path.exists() else 'missing'})")
    print(f"OG image:     {og_path} ({'ok' if og_path.exists() else 'missing'})")
    print(f"Pin image:    {pin_path} ({'ok' if pin_path.exists() else 'missing'})")
    if got_remote:
        print(f"Pexels credit: {credit_name} - {credit_url}")

if __name__ == "__main__":
    main()
