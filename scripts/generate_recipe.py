import os, re, random, textwrap
from datetime import datetime
from pathlib import Path

import yaml  # PyYAML
try:
    from PIL import Image, ImageDraw
    PIL_OK = True
except Exception:
    PIL_OK = False

# ------------- Settings -------------
POSTS_DIR = Path("_posts")
IMG_HERO_DIR = Path("assets/images")
IMG_OG_DIR = Path("assets/og")
IMG_PIN_DIR = Path("assets/pins")

CATEGORIES = ["creami", "frozen-treats", "protein-bakes", "seasonal"]
SITE_NAME = "Whip It Good"
BRAND_COLOR = (20, 20, 20)     # text color
BG_LIGHT = (248, 248, 248)     # hero bg
OG_BG = (242, 246, 255)        # og bg
PIN_BG = (255, 248, 242)       # pin bg
# ------------------------------------

# Base banks (merged/extended by _data/ideas.yml if present)
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
        ("Strawberry Cheesecake Protein Ice Cream", [
            "1 cup unsweetened almond milk",
            "1/2 cup nonfat Greek yogurt",
            "1 scoop vanilla whey or casein",
            "1/3 cup diced strawberries",
            "1 tbsp sugar-free cheesecake pudding mix",
            "1–2 tsp allulose",
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
        ("Blueberry Protein Muffins", [
            "1 cup oat flour",
            "1/2 cup vanilla whey/casein blend",
            "1 tsp baking powder",
            "1/4 cup allulose or sweetener",
            "2 large eggs",
            "3/4 cup nonfat Greek yogurt",
            "1/2 cup blueberries",
            "1 tsp vanilla extract",
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
        ("Peppermint Mocha Protein Ice Cream", [
            "1 cup unsweetened almond milk",
            "1/2 cup nonfat Greek yogurt",
            "1 scoop chocolate whey or casein",
            "1 tsp instant espresso powder",
            "1/8 tsp peppermint extract",
            "1–2 tsp allulose",
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
    "protein-bakes": [
        ("Dry texture", "Reduce bake time 2–3 minutes, add 1–2 tbsp yogurt, or use a whey/casein blend."),
        ("Rubbery crumb", "Avoid over-mixing once wet ingredients are added; use cocoa/oat flour balance."),
    ],
    "seasonal": [
        ("Muted spice flavor", "Increase spice 1/4 tsp at a time; salt amplifies sweetness and flavor."),
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
    for p in (POSTS_DIR, IMG_HERO_DIR, IMG_OG_DIR, IMG_PIN_DIR):
        p.mkdir(parents=True, exist_ok=True)

def load_ideas():
    """Reads optional _data/ideas.yml to extend banks."""
    ideas_path = Path("_data/ideas.yml")
    if not ideas_path.exists():
        return
    data = yaml.safe_load(ideas_path.read_text(encoding="utf-8")) or {}
    # Extend banks if provided
    if "subtitles" in data:
        SPINTAX_SUBTITLES.extend([str(x) for x in data["subtitles"]])
    if "descriptions" in data:
        SPINTAX_DESCS.extend([str(x) for x in data["descriptions"]])
    if "tips" in data:
        TIPS.extend([str(x) for x in data["tips"]])
    if "faq" in data:
        for q in data["faq"]:
            if isinstance(q, dict) and "q" in q and "a" in q:
                FAQ_BANK.append((str(q["q"]), str(q["a"])))
    if "flavors" in data:
        # flavors: { category_slug: [ [title, [ingredients...]], ... ] }
        for cat, items in data["flavors"].items():
            FLAVORS.setdefault(cat, [])
            for pair in items:
                if isinstance(pair, list) and len(pair) == 2:
                    title, ing = pair
                    FLAVORS[cat].append((str(title), [str(i) for i in ing]))

def macro_estimate(cat: str):
    if cat == "creami":           return ("160 kcal", "25 g", "8 g", "3 g")
    if cat == "frozen-treats":    return ("90 kcal", "10 g", "11 g", "1 g")
    if cat == "protein-bakes":    return ("150 kcal", "12 g", "16 g", "4 g")
    return ("160 kcal", "22 g", "14 g", "3 g")

def draw_card(w, h, bg, title, sub, outfile):
    if not PIL_OK: return
    img = Image.new("RGB", (w, h), color=bg)
    d = ImageDraw.Draw(img)
    # Simple text blocks (default bitmap font). Keep padding big for readability.
    y = 40
    d.text((40, y), SITE_NAME, fill=BRAND_COLOR); y += 60
    # wrap title to ~30 chars per line
    def wrap_text(t, width=30):
        return textwrap.fill(t, width=width)
    d.text((40, y), wrap_text(title, 28), fill=BRAND_COLOR); y += 160
    if sub:
        d.text((40, y), wrap_text(sub, 34), fill=(60, 60, 60))
    outfile.parent.mkdir(parents=True, exist_ok=True)
    img.save(outfile, "JPEG", quality=86, optimize=True)

def make_images(title, subtitle, slug):
    # Hero (page) 1200x800, OG 1200x630, Pin 1200x1800
    hero = IMG_HERO_DIR / f"{slug}.jpg"
    og = IMG_OG_DIR / f"{slug}-og.jpg"
    pin = IMG_PIN_DIR / f"{slug}-pin.jpg"
    if PIL_OK:
        draw_card(1200, 800, BG_LIGHT, title, subtitle, hero)
        draw_card(1200, 630, OG_BG, title, subtitle, og)
        draw_card(1200, 1800, PIN_BG, title, subtitle, pin)
    return hero, og, pin

def build_sections(cat, title):
    # Tips
    tips = random.sample(TIPS, k=min(3, len(TIPS)))
    # Variations (simple templated ideas)
    variations = [
        "Swap whey for a whey/casein blend to improve texture.",
        "Use allulose for softer freeze; erythritol sets harder.",
        "Add 1–2 tbsp nonfat Greek yogurt for creaminess.",
        "Stir in mix-ins after the first spin (chips, berries, cookie crumbles).",
    ]
    # Troubleshooting
    ts_list = TROUBLESHOOT.get(cat, [])
    # FAQs (pick 2)
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

def main():
    ensure_dirs()
    load_ideas()

    cat = random.choice(CATEGORIES)
    title, ingredients = random.choice(FLAVORS[cat])
    treat_word = "treat" if cat != "protein-bakes" else "bake"
    subtitle = spin(random.choice(SPINTAX_SUBTITLES)).replace("{treat}", treat_word)
    description = spin(random.choice(SPINTAX_DESCS)).replace("{treat}", treat_word)

    steps = INSTRUCTIONS[cat]
    calories,
