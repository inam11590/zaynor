"""Seed script — populates the database with ZAYNOR's initial product catalog
and creates a default admin user.

Run from the backend/ directory:
    python -m app.seed
"""

import json

from app.database import Base, SessionLocal, engine
from app.models import Category, Product
from app.models.user import User
from app.services.auth import hash_password

# ---------------------------------------------------------------------------
# Category definitions
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"name": "Perfumes & Attars", "slug": "perfumes"},
    {"name": "Skin Care", "slug": "skincare"},
]

# ---------------------------------------------------------------------------
# Product data — migrated from js/script.js PRODUCTS object
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ── Perfumes ────────────────────────────────────────────────────────
    {
        "slug": "monarch-intense",
        "name": "Monarch Intense",
        "price": 4500,
        "image": "images/perfumes/monarch.png",
        "short_description": "A sophisticated blend of warm amber, royal oud, and smoky vetiver designed for the modern gentleman.",
        "description": (
            "Monarch Intense is our signature fragrance. Crafted for the modern Pakistani gentleman "
            "who commands presence, it blends rich traditional notes with contemporary sophistication. "
            "It opens with striking notes of fresh bergamot and pink pepper, transitioning into a warm "
            "heart of royal oud and cedarwood, and settles into an enduring, powerful base of amber, "
            "tobacco, and oakmoss."
        ),
        "specs": {
            "Longevity": "12+ Hours (Extrait de Parfum)",
            "Notes": "Amber, Royal Oud, Warm Leather, Vetiver",
            "Volume": "50 ml",
            "Best For": "Evening wear & formal occasions",
        },
        "category_slug": "perfumes",
    },
    {
        "slug": "obsidian-oud",
        "name": "Obsidian Oud",
        "price": 4800,
        "image": "images/perfumes/obsidian.png",
        "short_description": "An enigmatic, deep fragrance centered around dark wood notes, premium musk, and spicy cardamom.",
        "description": (
            "Obsidian Oud is a mysterious and captivating fragrance, designed for those who appreciate "
            "the finer things in life. This scent is built around the raw, intense aroma of rare dark "
            "agarwood, accented by notes of freshly crushed cardamom, sweet vanilla pod, and rich "
            "sandalwood. It offers a warm, enveloping trail that leaves an unforgettable impression."
        ),
        "specs": {
            "Longevity": "10+ Hours (Extrait de Parfum)",
            "Notes": "Dark Agarwood, Premium Musk, Cardamom, Sandalwood",
            "Volume": "50 ml",
            "Best For": "Signature scent / All-season night",
        },
        "category_slug": "perfumes",
    },
    {
        "slug": "royal-safari",
        "name": "Royal Safari",
        "price": 3800,
        "image": "images/perfumes/safari.png",
        "short_description": "A refreshing, long-lasting concentrated attar featuring fresh citrus, white musk, and patchouli.",
        "description": (
            "Royal Safari is a premium concentrated perfume oil (attar) that brings the freshness of "
            "the outdoors directly to your grooming routine. Starting with high-energy citrus notes of "
            "green mandarin and bergamot, it leads into a heart of fresh herbs and lavender, anchored "
            "by a premium base of patchouli, white musk, and soft cedar. Alcohol-free and skin-friendly."
        ),
        "specs": {
            "Longevity": "8-10 Hours (Concentrated Attar)",
            "Notes": "Green Mandarin, Lavender, White Musk, Patchouli",
            "Volume": "12 ml (Attar)",
            "Best For": "Day wear / Post-grooming freshness",
        },
        "category_slug": "perfumes",
    },
    {
        "slug": "kashmir-wood",
        "name": "Kashmir Wood",
        "price": 4200,
        "image": "images/perfumes/monarch.png",
        "short_description": "A rich, woody fragrance inspired by the crisp pine forests and cedar valleys of Kashmir.",
        "description": (
            "Kashmir Wood captures the spirit of northern Pakistan. It's a crisp, green, and deeply "
            "woody fragrance that brings to life the clean air of pine forests and Himalayan cedar "
            "valleys. Hearty base notes of earth, wet soil, and pine resin are brightened by light "
            "top notes of cypress and wild juniper berry."
        ),
        "specs": {
            "Longevity": "8-10 Hours (Eau de Parfum)",
            "Notes": "Cypress, Juniper Berry, Himalayan Cedar, Wet Earth",
            "Volume": "50 ml",
            "Best For": "Day wear / Autumn & Winter",
        },
        "category_slug": "perfumes",
    },
    {
        "slug": "sultan-gold",
        "name": "Sultan Gold",
        "price": 4999,
        "image": "images/perfumes/safari.png",
        "short_description": "A warm, opulent perfume oil blending sweet honey, oriental spices, and aged white oud.",
        "description": (
            "Sultan Gold is a truly royal attar, crafted for special occasions. It is a dense, warm, "
            "and highly comforting blend. Notes of rich honey and roasted almonds interlace with "
            "Turkish rose and a base of fine aged white oud, rich amber, and vanilla. A classic "
            "unisex blend with intense projections."
        ),
        "specs": {
            "Longevity": "12-14 Hours (Concentrated Attar)",
            "Notes": "Honey, Spiced Almond, Turkish Rose, White Oud",
            "Volume": "12 ml (Attar)",
            "Best For": "Weddings / Special gatherings",
        },
        "category_slug": "perfumes",
    },
    {
        "slug": "lahore-nights",
        "name": "Lahore Nights",
        "price": 4600,
        "image": "images/perfumes/obsidian.png",
        "short_description": "An alluring, sensual night-out perfume with spicy pink pepper, tonka bean, and tobacco.",
        "description": (
            "Lahore Nights is vibrant, electric, and full of life — much like the cultural heart of "
            "Pakistan. This fragrance is designed for unforgettable nights. Spicy top notes of pink "
            "pepper and ginger give way to a smooth, sweet heart of tonka bean and vanilla, settled on "
            "a strong base of golden honeyed tobacco leaf and dark vetiver."
        ),
        "specs": {
            "Longevity": "10+ Hours (Extrait de Parfum)",
            "Notes": "Pink Pepper, Tonka Bean, Sweet Tobacco, Vetiver",
            "Volume": "50 ml",
            "Best For": "Night outs / Street wear",
        },
        "category_slug": "perfumes",
    },

    # ── Skincare ────────────────────────────────────────────────────────
    {
        "slug": "activated-charcoal-face-wash",
        "name": "Activated Charcoal Face Wash",
        "price": 1200,
        "image": "images/skincare/facewash.png",
        "short_description": "Deeply detoxifying face wash that lifts impurities, regulates sebum, and prevents breakouts.",
        "description": (
            "ZAYNOR Activated Charcoal Face Wash is engineered specifically for men's thicker, oilier "
            "skin. Formulated with premium activated charcoal beads, it acts like a magnet to extract "
            "deep-seated dirt, pollution particles, and excess oils. Enriched with natural Aloe Vera "
            "and tea tree extracts to soothe skin and prevent acne without stripping natural moisture."
        ),
        "specs": {
            "Skin Type": "Oily, Acne-Prone & Combination Skin",
            "Key Ingredients": "Activated Charcoal, Tea Tree Oil, Aloe Vera Extract",
            "Volume": "150 ml",
            "Usage": "Twice daily (Morning & Night)",
        },
        "category_slug": "skincare",
    },
    {
        "slug": "elixir-hydrating-serum",
        "name": "Elixir Hydrating Serum",
        "price": 1850,
        "image": "images/skincare/serum.png",
        "short_description": "Advanced Hyaluronic Acid & Vitamin B5 serum for intense hydration and plump, youthful skin.",
        "description": (
            "Our Elixir Hydrating Serum is a lightweight, non-greasy formula that penetrates deep into "
            "skin layers. It combines multi-weight Hyaluronic Acid molecules with Vitamin B5 (Panthenol) "
            "to lock in hydration, smooth out fine lines, and rebuild skin barriers damaged by shaving, "
            "pollution, or sun exposure. Instantly refreshes tired skin."
        ),
        "specs": {
            "Skin Type": "All Skin Types (highly recommended for dry/dull skin)",
            "Key Ingredients": "Hyaluronic Acid (2%), Vitamin B5, Green Tea Extract",
            "Volume": "30 ml",
            "Usage": "3-4 drops daily on clean, damp skin",
        },
        "category_slug": "skincare",
    },
    {
        "slug": "royal-beard-growth-oil",
        "name": "Royal Beard Growth Oil",
        "price": 1500,
        "image": "images/skincare/serum.png",
        "short_description": "Premium blend of organic oils to soften hair, soothe itchy skin, and promote beard growth.",
        "description": (
            "ZAYNOR Beard Growth Oil is a premium elixir containing cold-pressed organic jojoba, argan, "
            "and sweet almond oils. Specially formulated to nourish hair follicles, eliminate 'beard "
            "dandruff', soothe dry skin, and stimulate healthy beard growth. Infused with a light "
            "signature scent of cedar and citrus that stays all day."
        ),
        "specs": {
            "Hair Type": "All Beard Types & Lengths",
            "Key Ingredients": "Jojoba Oil, Moroccan Argan Oil, Sweet Almond Oil, Cedarwood",
            "Volume": "30 ml",
            "Usage": "Once daily after shower (3-5 drops)",
        },
        "category_slug": "skincare",
    },
    {
        "slug": "himalayan-mineral-clay-mask",
        "name": "Himalayan Mineral Clay Mask",
        "price": 1600,
        "image": "images/skincare/facewash.png",
        "short_description": "Purifying clay mask that shrinks pores, controls shine, and brightens skin tone.",
        "description": (
            "This mineral-rich clay mask draws out toxins from deep within the skin. Utilizing pure "
            "bentonite clay sourced from the foothill minerals of the Himalayas, combined with kaolin "
            "clay and soothing eucalyptus leaf oil. It effectively shrinks dilated pores, controls "
            "greasy shine, and improves skin texture for an instant brightened complexion."
        ),
        "specs": {
            "Skin Type": "Oily & Congested Skin",
            "Key Ingredients": "Himalayan Bentonite Clay, Kaolin, Eucalyptus Oil",
            "Volume": "100 g",
            "Usage": "1-2 times weekly (Leave on for 10 minutes)",
        },
        "category_slug": "skincare",
    },
    {
        "slug": "hydro-boost-gel-cream",
        "name": "Hydro-Boost Gel Cream",
        "price": 1950,
        "image": "images/skincare/serum.png",
        "short_description": "Ultra-lightweight oil-free face moisturizer that absorbs instantly for 24-hour hydration.",
        "description": (
            "ZAYNOR Hydro-Boost is an oil-free, gel-based moisturizer designed specifically for men who "
            "hate the sticky feeling of traditional creams. Formulated with cooling Cucumber water, "
            "Niacinamide, and Centella Asiatica (Cica). It repairs the skin barrier, reduces redness "
            "from razor burns, and keeps skin matte yet thoroughly hydrated all day."
        ),
        "specs": {
            "Skin Type": "Normal, Oily, and Combination Skin",
            "Key Ingredients": "Niacinamide, Centella Asiatica, Cucumber Hydrosol",
            "Volume": "50 ml",
            "Usage": "Apply twice daily on clean face and neck",
        },
        "category_slug": "skincare",
    },
    {
        "slug": "salicylic-acid-clarifying-toner",
        "name": "Salicylic Acid Clarifying Toner",
        "price": 1400,
        "image": "images/skincare/facewash.png",
        "short_description": "Gently exfoliating toner containing 2% BHA to clear blackheads and prevent acne.",
        "description": (
            "Our clarifying toner features 2% Salicylic Acid (BHA), a fat-soluble acid that penetrates "
            "deep into pores to dissolve oil clogs, dead skin cells, and blackheads. Blended with "
            "witch hazel and chamomile extract to calm irritation and keep skin fresh, clear, and "
            "perfectly balanced."
        ),
        "specs": {
            "Skin Type": "Acne-Prone & Highly Congested Skin",
            "Key Ingredients": "Salicylic Acid (BHA 2%), Witch Hazel, Chamomile Extract",
            "Volume": "120 ml",
            "Usage": "Apply with cotton pad once daily at night",
        },
        "category_slug": "skincare",
    },
]


def seed():
    """Create tables and insert seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Admin user ─────────────────────────────────────────────────
        admin_email = "admin@zaynor.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=hash_password("admin123"),
                is_admin=True,
            )
            db.add(admin)
            db.flush()
            print(f"  + Created admin user: {admin_email} / admin123")
        else:
            print(f"  ~ Admin user already exists: {admin_email}")

        # ── Categories ──────────────────────────────────────────────────
        category_map: dict[str, int] = {}
        for cat_data in CATEGORIES:
            existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if existing:
                category_map[cat_data["slug"]] = existing.id
            else:
                category = Category(**cat_data)
                db.add(category)
                db.flush()  # get the ID without committing
                category_map[cat_data["slug"]] = category.id
                print(f"  + Created category: {cat_data['name']}")

        # ── Products ────────────────────────────────────────────────────
        for prod_data in PRODUCTS:
            slug = prod_data["slug"]
            cat_slug = prod_data.pop("category_slug")

            existing = db.query(Product).filter(Product.slug == slug).first()
            if existing:
                print(f"  ~ Already exists: {prod_data['name']}")
                continue

            product = Product(
                slug=slug,
                name=prod_data["name"],
                price=prod_data["price"],
                image=prod_data["image"],
                short_description=prod_data["short_description"],
                description=prod_data["description"],
                specs=json.dumps(prod_data["specs"]),
                category_id=category_map[cat_slug],
            )
            db.add(product)
            print(f"  + Created product: {prod_data['name']}")

        db.commit()
        print(f"\nSeed complete: 1 admin user, {len(CATEGORIES)} categories, {len(PRODUCTS)} products.")

    except Exception as e:
        db.rollback()
        print(f"\nError during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("ZAYNOR — Database Seed Script\n")
    seed()
