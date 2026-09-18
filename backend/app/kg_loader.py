"""
ShopGraph - Knowledge Graph Loader
app/kg_loader.py

Loads all nodes and relationships into Neo4j using MERGE statements.
This module is used by scripts/load_kg.py.
"""

from app.database import Neo4jConnection


# ── Raw Data ─────────────────────────────────────────────────────────────────

CATEGORIES = [
    {"name": "Laptop",       "description": "Portable personal computers"},
    {"name": "Mouse",        "description": "Pointing input devices"},
    {"name": "Keyboard",     "description": "Text input devices"},
    {"name": "USB Hub",      "description": "Multi-port USB connectivity adapters"},
    {"name": "Laptop Stand", "description": "Ergonomic stands for laptops"},
    {"name": "Laptop Bag",   "description": "Carrying cases for laptops"},
    {"name": "Monitor",      "description": "External display screens"},
    {"name": "Headphones",   "description": "Personal audio devices"},
    {"name": "Storage",      "description": "External data storage devices"},
    {"name": "Webcam",       "description": "Video capture devices for conferencing"},
]

FEATURES = [
    {"name": "USB-C",             "description": "Supports USB Type-C connectivity"},
    {"name": "Bluetooth",         "description": "Wireless Bluetooth connectivity"},
    {"name": "Wireless",          "description": "Wire-free operation"},
    {"name": "HDMI",              "description": "HDMI video output support"},
    {"name": "WiFi",              "description": "Built-in wireless internet"},
    {"name": "Portable",          "description": "Compact and travel-friendly design"},
    {"name": "Noise Cancellation","description": "Active noise cancellation technology"},
    {"name": "Mechanical Keys",   "description": "Mechanical key switches"},
    {"name": "Ergonomic",         "description": "Designed for comfort and reduced strain"},
    {"name": "1TB Storage",       "description": "One terabyte of storage capacity"},
]

BRANDS = [
    {"name": "Dell",       "country": "USA"},
    {"name": "HP",         "country": "USA"},
    {"name": "Lenovo",     "country": "China"},
    {"name": "Logitech",   "country": "Switzerland"},
    {"name": "Keychron",   "country": "USA"},
    {"name": "Anker",      "country": "USA"},
    {"name": "Sony",       "country": "Japan"},
    {"name": "JBL",        "country": "USA"},
    {"name": "Samsung",    "country": "South Korea"},
    {"name": "LG",         "country": "South Korea"},
    {"name": "WD",         "country": "USA"},
    {"name": "Portronics", "country": "India"},
]

USE_CASES = [
    {"name": "Programming",        "description": "Software development and coding work"},
    {"name": "Office Work",        "description": "General office productivity tasks"},
    {"name": "Gaming",             "description": "Video gaming and esports"},
    {"name": "Work From Home",     "description": "Remote work and home office setup"},
    {"name": "Entertainment",      "description": "Media consumption and leisure"},
    {"name": "Travel",             "description": "On-the-go mobile use"},
    {"name": "Video Conferencing", "description": "Online meetings and video calls"},
    {"name": "Content Creation",   "description": "Digital content production and editing"},
]

PRODUCTS = [
    {"name": "Dell Inspiron 15",       "price": 55000, "description": "15-inch laptop suitable for everyday computing and programming"},
    {"name": "HP Pavilion 15",          "price": 52000, "description": "15-inch HP laptop with great performance and battery life"},
    {"name": "Lenovo IdeaPad Slim 5",   "price": 57000, "description": "Slim 15-inch laptop with excellent keyboard and display"},
    {"name": "Logitech MX Master 3S",   "price": 9000,  "description": "Advanced wireless ergonomic mouse for professionals"},
    {"name": "Logitech M331",           "price": 2500,  "description": "Silent wireless mouse for everyday use"},
    {"name": "Keychron K2",             "price": 7500,  "description": "Compact mechanical keyboard with Bluetooth and hot-swap support"},
    {"name": "Logitech K380",           "price": 3500,  "description": "Compact multi-device Bluetooth keyboard"},
    {"name": "Dell USB-C Hub",          "price": 4500,  "description": "7-in-1 USB-C hub with HDMI and USB ports"},
    {"name": "Anker USB-C Hub",         "price": 3500,  "description": "Compact 6-in-1 USB-C hub with power delivery"},
    {"name": "Dell Laptop Stand",       "price": 3000,  "description": "Adjustable aluminum laptop stand for ergonomic setup"},
    {"name": "Portronics Laptop Stand", "price": 1500,  "description": "Portable foldable laptop stand for desk or travel"},
    {"name": "Dell Laptop Bag",         "price": 2500,  "description": "Durable 15-inch laptop bag with multiple compartments"},
    {"name": "HP Laptop Backpack",      "price": 2000,  "description": "Water-resistant 15.6-inch laptop backpack"},
    {"name": "LG 24 inch Monitor",      "price": 15000, "description": "24-inch IPS FHD monitor with USB-C and HDMI"},
    {"name": "Dell 24 inch Monitor",    "price": 16000, "description": "24-inch IPS monitor with anti-glare screen and HDMI"},
    {"name": "Sony WH-1000XM5",         "price": 29000, "description": "Industry-leading noise cancelling wireless headphones"},
    {"name": "JBL Tune 770NC",          "price": 8000,  "description": "Adaptive noise cancelling wireless headphones"},
    {"name": "Samsung T7 SSD 1TB",      "price": 8500,  "description": "Portable SSD with USB-C and fast transfer speeds"},
    {"name": "WD My Passport 1TB",      "price": 4500,  "description": "Compact USB-C portable hard drive"},
    {"name": "Logitech C920 Webcam",    "price": 7000,  "description": "Full HD 1080p webcam for video conferencing"},
]

# (source_product, relationship_type, target)
# For BELONGS_TO and MADE_BY, target is Category/Brand name.
# For HAS_FEATURE and USED_FOR, target is Feature/UseCase name.
# For product-to-product rels, target is Product name.
PRODUCT_RELATIONS = [
    # BELONGS_TO
    ("Dell Inspiron 15",       "BELONGS_TO", "Laptop"),
    ("HP Pavilion 15",          "BELONGS_TO", "Laptop"),
    ("Lenovo IdeaPad Slim 5",   "BELONGS_TO", "Laptop"),
    ("Logitech MX Master 3S",   "BELONGS_TO", "Mouse"),
    ("Logitech M331",           "BELONGS_TO", "Mouse"),
    ("Keychron K2",             "BELONGS_TO", "Keyboard"),
    ("Logitech K380",           "BELONGS_TO", "Keyboard"),
    ("Dell USB-C Hub",          "BELONGS_TO", "USB Hub"),
    ("Anker USB-C Hub",         "BELONGS_TO", "USB Hub"),
    ("Dell Laptop Stand",       "BELONGS_TO", "Laptop Stand"),
    ("Portronics Laptop Stand", "BELONGS_TO", "Laptop Stand"),
    ("Dell Laptop Bag",         "BELONGS_TO", "Laptop Bag"),
    ("HP Laptop Backpack",      "BELONGS_TO", "Laptop Bag"),
    ("LG 24 inch Monitor",      "BELONGS_TO", "Monitor"),
    ("Dell 24 inch Monitor",    "BELONGS_TO", "Monitor"),
    ("Sony WH-1000XM5",         "BELONGS_TO", "Headphones"),
    ("JBL Tune 770NC",          "BELONGS_TO", "Headphones"),
    ("Samsung T7 SSD 1TB",      "BELONGS_TO", "Storage"),
    ("WD My Passport 1TB",      "BELONGS_TO", "Storage"),
    ("Logitech C920 Webcam",    "BELONGS_TO", "Webcam"),
    # MADE_BY
    ("Dell Inspiron 15",       "MADE_BY", "Dell"),
    ("HP Pavilion 15",          "MADE_BY", "HP"),
    ("Lenovo IdeaPad Slim 5",   "MADE_BY", "Lenovo"),
    ("Logitech MX Master 3S",   "MADE_BY", "Logitech"),
    ("Logitech M331",           "MADE_BY", "Logitech"),
    ("Keychron K2",             "MADE_BY", "Keychron"),
    ("Logitech K380",           "MADE_BY", "Logitech"),
    ("Dell USB-C Hub",          "MADE_BY", "Dell"),
    ("Anker USB-C Hub",         "MADE_BY", "Anker"),
    ("Dell Laptop Stand",       "MADE_BY", "Dell"),
    ("Portronics Laptop Stand", "MADE_BY", "Portronics"),
    ("Dell Laptop Bag",         "MADE_BY", "Dell"),
    ("HP Laptop Backpack",      "MADE_BY", "HP"),
    ("LG 24 inch Monitor",      "MADE_BY", "LG"),
    ("Dell 24 inch Monitor",    "MADE_BY", "Dell"),
    ("Sony WH-1000XM5",         "MADE_BY", "Sony"),
    ("JBL Tune 770NC",          "MADE_BY", "JBL"),
    ("Samsung T7 SSD 1TB",      "MADE_BY", "Samsung"),
    ("WD My Passport 1TB",      "MADE_BY", "WD"),
    ("Logitech C920 Webcam",    "MADE_BY", "Logitech"),
    # HAS_FEATURE
    ("Dell Inspiron 15",       "HAS_FEATURE", "USB-C"),
    ("Dell Inspiron 15",       "HAS_FEATURE", "Bluetooth"),
    ("Dell Inspiron 15",       "HAS_FEATURE", "WiFi"),
    ("HP Pavilion 15",          "HAS_FEATURE", "USB-C"),
    ("HP Pavilion 15",          "HAS_FEATURE", "Bluetooth"),
    ("HP Pavilion 15",          "HAS_FEATURE", "WiFi"),
    ("Lenovo IdeaPad Slim 5",   "HAS_FEATURE", "USB-C"),
    ("Lenovo IdeaPad Slim 5",   "HAS_FEATURE", "Bluetooth"),
    ("Lenovo IdeaPad Slim 5",   "HAS_FEATURE", "WiFi"),
    ("Logitech MX Master 3S",   "HAS_FEATURE", "Bluetooth"),
    ("Logitech MX Master 3S",   "HAS_FEATURE", "Wireless"),
    ("Logitech MX Master 3S",   "HAS_FEATURE", "Ergonomic"),
    ("Logitech M331",           "HAS_FEATURE", "Wireless"),
    ("Logitech M331",           "HAS_FEATURE", "Portable"),
    ("Keychron K2",             "HAS_FEATURE", "Bluetooth"),
    ("Keychron K2",             "HAS_FEATURE", "Wireless"),
    ("Keychron K2",             "HAS_FEATURE", "Mechanical Keys"),
    ("Logitech K380",           "HAS_FEATURE", "Bluetooth"),
    ("Logitech K380",           "HAS_FEATURE", "Wireless"),
    ("Logitech K380",           "HAS_FEATURE", "Portable"),
    ("Dell USB-C Hub",          "HAS_FEATURE", "USB-C"),
    ("Dell USB-C Hub",          "HAS_FEATURE", "HDMI"),
    ("Anker USB-C Hub",         "HAS_FEATURE", "USB-C"),
    ("Anker USB-C Hub",         "HAS_FEATURE", "HDMI"),
    ("Anker USB-C Hub",         "HAS_FEATURE", "Portable"),
    ("Dell Laptop Stand",       "HAS_FEATURE", "Ergonomic"),
    ("Portronics Laptop Stand", "HAS_FEATURE", "Portable"),
    ("Portronics Laptop Stand", "HAS_FEATURE", "Ergonomic"),
    ("LG 24 inch Monitor",      "HAS_FEATURE", "USB-C"),
    ("LG 24 inch Monitor",      "HAS_FEATURE", "HDMI"),
    ("Dell 24 inch Monitor",    "HAS_FEATURE", "HDMI"),
    ("Sony WH-1000XM5",         "HAS_FEATURE", "Bluetooth"),
    ("Sony WH-1000XM5",         "HAS_FEATURE", "Wireless"),
    ("Sony WH-1000XM5",         "HAS_FEATURE", "Noise Cancellation"),
    ("JBL Tune 770NC",          "HAS_FEATURE", "Bluetooth"),
    ("JBL Tune 770NC",          "HAS_FEATURE", "Wireless"),
    ("JBL Tune 770NC",          "HAS_FEATURE", "Noise Cancellation"),
    ("JBL Tune 770NC",          "HAS_FEATURE", "Portable"),
    ("Samsung T7 SSD 1TB",      "HAS_FEATURE", "USB-C"),
    ("Samsung T7 SSD 1TB",      "HAS_FEATURE", "Portable"),
    ("Samsung T7 SSD 1TB",      "HAS_FEATURE", "1TB Storage"),
    ("WD My Passport 1TB",      "HAS_FEATURE", "USB-C"),
    ("WD My Passport 1TB",      "HAS_FEATURE", "Portable"),
    ("WD My Passport 1TB",      "HAS_FEATURE", "1TB Storage"),
    ("Logitech C920 Webcam",    "HAS_FEATURE", "Portable"),
    # USED_FOR
    ("Dell Inspiron 15",       "USED_FOR", "Programming"),
    ("Dell Inspiron 15",       "USED_FOR", "Office Work"),
    ("Dell Inspiron 15",       "USED_FOR", "Work From Home"),
    ("HP Pavilion 15",          "USED_FOR", "Programming"),
    ("HP Pavilion 15",          "USED_FOR", "Office Work"),
    ("HP Pavilion 15",          "USED_FOR", "Entertainment"),
    ("Lenovo IdeaPad Slim 5",   "USED_FOR", "Programming"),
    ("Lenovo IdeaPad Slim 5",   "USED_FOR", "Office Work"),
    ("Lenovo IdeaPad Slim 5",   "USED_FOR", "Work From Home"),
    ("Logitech MX Master 3S",   "USED_FOR", "Programming"),
    ("Logitech MX Master 3S",   "USED_FOR", "Office Work"),
    ("Logitech MX Master 3S",   "USED_FOR", "Content Creation"),
    ("Logitech M331",           "USED_FOR", "Office Work"),
    ("Logitech M331",           "USED_FOR", "Work From Home"),
    ("Keychron K2",             "USED_FOR", "Programming"),
    ("Keychron K2",             "USED_FOR", "Gaming"),
    ("Keychron K2",             "USED_FOR", "Office Work"),
    ("Logitech K380",           "USED_FOR", "Office Work"),
    ("Logitech K380",           "USED_FOR", "Work From Home"),
    ("Logitech K380",           "USED_FOR", "Travel"),
    ("Dell USB-C Hub",          "USED_FOR", "Office Work"),
    ("Dell USB-C Hub",          "USED_FOR", "Work From Home"),
    ("Anker USB-C Hub",         "USED_FOR", "Office Work"),
    ("Anker USB-C Hub",         "USED_FOR", "Work From Home"),
    ("Anker USB-C Hub",         "USED_FOR", "Travel"),
    ("Dell Laptop Stand",       "USED_FOR", "Office Work"),
    ("Dell Laptop Stand",       "USED_FOR", "Work From Home"),
    ("Portronics Laptop Stand", "USED_FOR", "Office Work"),
    ("Portronics Laptop Stand", "USED_FOR", "Travel"),
    ("LG 24 inch Monitor",      "USED_FOR", "Programming"),
    ("LG 24 inch Monitor",      "USED_FOR", "Office Work"),
    ("LG 24 inch Monitor",      "USED_FOR", "Gaming"),
    ("Dell 24 inch Monitor",    "USED_FOR", "Programming"),
    ("Dell 24 inch Monitor",    "USED_FOR", "Office Work"),
    ("Dell 24 inch Monitor",    "USED_FOR", "Work From Home"),
    ("Sony WH-1000XM5",         "USED_FOR", "Entertainment"),
    ("Sony WH-1000XM5",         "USED_FOR", "Travel"),
    ("Sony WH-1000XM5",         "USED_FOR", "Office Work"),
    ("JBL Tune 770NC",          "USED_FOR", "Entertainment"),
    ("JBL Tune 770NC",          "USED_FOR", "Travel"),
    ("JBL Tune 770NC",          "USED_FOR", "Office Work"),
    ("Samsung T7 SSD 1TB",      "USED_FOR", "Programming"),
    ("Samsung T7 SSD 1TB",      "USED_FOR", "Content Creation"),
    ("WD My Passport 1TB",      "USED_FOR", "Office Work"),
    ("WD My Passport 1TB",      "USED_FOR", "Travel"),
    ("Logitech C920 Webcam",    "USED_FOR", "Video Conferencing"),
    ("Logitech C920 Webcam",    "USED_FOR", "Content Creation"),
    ("Logitech C920 Webcam",    "USED_FOR", "Work From Home"),
]

# Product-to-product relationships only
PRODUCT_PRODUCT_RELATIONS = [
    # COMPATIBLE_WITH
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Logitech MX Master 3S"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Logitech M331"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Keychron K2"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Logitech K380"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Dell USB-C Hub"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Anker USB-C Hub"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "Samsung T7 SSD 1TB"),
    ("Dell Inspiron 15",       "COMPATIBLE_WITH", "WD My Passport 1TB"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Logitech MX Master 3S"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Logitech M331"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Keychron K2"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Logitech K380"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Anker USB-C Hub"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "Samsung T7 SSD 1TB"),
    ("HP Pavilion 15",          "COMPATIBLE_WITH", "WD My Passport 1TB"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "Logitech MX Master 3S"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "Keychron K2"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "Logitech K380"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "Anker USB-C Hub"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "Samsung T7 SSD 1TB"),
    ("Lenovo IdeaPad Slim 5",   "COMPATIBLE_WITH", "WD My Passport 1TB"),
    # ACCESSORY
    ("Dell Inspiron 15",       "ACCESSORY", "Dell Laptop Stand"),
    ("Dell Inspiron 15",       "ACCESSORY", "Portronics Laptop Stand"),
    ("Dell Inspiron 15",       "ACCESSORY", "Dell Laptop Bag"),
    ("Dell Inspiron 15",       "ACCESSORY", "HP Laptop Backpack"),
    ("HP Pavilion 15",          "ACCESSORY", "Portronics Laptop Stand"),
    ("HP Pavilion 15",          "ACCESSORY", "HP Laptop Backpack"),
    ("Lenovo IdeaPad Slim 5",   "ACCESSORY", "Portronics Laptop Stand"),
    ("Lenovo IdeaPad Slim 5",   "ACCESSORY", "Dell Laptop Bag"),
    # WORKS_WITH
    ("Dell Inspiron 15",       "WORKS_WITH", "Dell 24 inch Monitor"),
    ("Dell Inspiron 15",       "WORKS_WITH", "LG 24 inch Monitor"),
    ("Dell Inspiron 15",       "WORKS_WITH", "Logitech C920 Webcam"),
    ("HP Pavilion 15",          "WORKS_WITH", "LG 24 inch Monitor"),
    ("HP Pavilion 15",          "WORKS_WITH", "Logitech C920 Webcam"),
    ("Lenovo IdeaPad Slim 5",   "WORKS_WITH", "LG 24 inch Monitor"),
    ("Lenovo IdeaPad Slim 5",   "WORKS_WITH", "Dell 24 inch Monitor"),
    ("Lenovo IdeaPad Slim 5",   "WORKS_WITH", "Logitech C920 Webcam"),
    # SIMILAR_TO
    ("Dell Inspiron 15",       "SIMILAR_TO", "HP Pavilion 15"),
    ("Dell Inspiron 15",       "SIMILAR_TO", "Lenovo IdeaPad Slim 5"),
    ("HP Pavilion 15",          "SIMILAR_TO", "Dell Inspiron 15"),
    ("HP Pavilion 15",          "SIMILAR_TO", "Lenovo IdeaPad Slim 5"),
    ("Lenovo IdeaPad Slim 5",   "SIMILAR_TO", "Dell Inspiron 15"),
    ("Lenovo IdeaPad Slim 5",   "SIMILAR_TO", "HP Pavilion 15"),
    ("Logitech MX Master 3S",   "SIMILAR_TO", "Logitech M331"),
    ("Logitech M331",           "SIMILAR_TO", "Logitech MX Master 3S"),
    ("Keychron K2",             "SIMILAR_TO", "Logitech K380"),
    ("Logitech K380",           "SIMILAR_TO", "Keychron K2"),
    ("Dell USB-C Hub",          "SIMILAR_TO", "Anker USB-C Hub"),
    ("Anker USB-C Hub",         "SIMILAR_TO", "Dell USB-C Hub"),
    ("Dell Laptop Stand",       "SIMILAR_TO", "Portronics Laptop Stand"),
    ("Portronics Laptop Stand", "SIMILAR_TO", "Dell Laptop Stand"),
    ("LG 24 inch Monitor",      "SIMILAR_TO", "Dell 24 inch Monitor"),
    ("Dell 24 inch Monitor",    "SIMILAR_TO", "LG 24 inch Monitor"),
    ("Sony WH-1000XM5",         "SIMILAR_TO", "JBL Tune 770NC"),
    ("JBL Tune 770NC",          "SIMILAR_TO", "Sony WH-1000XM5"),
    ("Samsung T7 SSD 1TB",      "SIMILAR_TO", "WD My Passport 1TB"),
    ("WD My Passport 1TB",      "SIMILAR_TO", "Samsung T7 SSD 1TB"),
]


# ── Loader Functions ──────────────────────────────────────────────────────────

def create_constraints(db: Neo4jConnection) -> None:
    """Create uniqueness constraints for all node labels."""
    constraints = [
        ("Product", "name", "product_name_unique"),
        ("Category", "name", "category_name_unique"),
        ("Feature", "name", "feature_name_unique"),
        ("Brand", "name", "brand_name_unique"),
        ("UseCase", "name", "usecase_name_unique"),
    ]
    for label, prop, constraint_name in constraints:
        db.run_query(
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
        )
    print("✅ Constraints created")


def load_categories(db: Neo4jConnection) -> int:
    """Merge Category nodes into the graph."""
    for cat in CATEGORIES:
        db.run_query(
            "MERGE (c:Category {name: $name}) SET c.description = $description",
            {"name": cat["name"], "description": cat["description"]},
        )
    print(f"✅ Categories inserted: {len(CATEGORIES)}")
    return len(CATEGORIES)


def load_features(db: Neo4jConnection) -> int:
    """Merge Feature nodes into the graph."""
    for feat in FEATURES:
        db.run_query(
            "MERGE (f:Feature {name: $name}) SET f.description = $description",
            {"name": feat["name"], "description": feat["description"]},
        )
    print(f"✅ Features inserted: {len(FEATURES)}")
    return len(FEATURES)


def load_brands(db: Neo4jConnection) -> int:
    """Merge Brand nodes into the graph."""
    for brand in BRANDS:
        db.run_query(
            "MERGE (b:Brand {name: $name}) SET b.country = $country",
            {"name": brand["name"], "country": brand["country"]},
        )
    print(f"✅ Brands inserted: {len(BRANDS)}")
    return len(BRANDS)


def load_use_cases(db: Neo4jConnection) -> int:
    """Merge UseCase nodes into the graph."""
    for uc in USE_CASES:
        db.run_query(
            "MERGE (u:UseCase {name: $name}) SET u.description = $description",
            {"name": uc["name"], "description": uc["description"]},
        )
    print(f"✅ Use cases inserted: {len(USE_CASES)}")
    return len(USE_CASES)


def load_products(db: Neo4jConnection) -> int:
    """Merge Product nodes into the graph."""
    for product in PRODUCTS:
        db.run_query(
            "MERGE (p:Product {name: $name}) "
            "SET p.price = $price, p.description = $description",
            {"name": product["name"], "price": product["price"],
             "description": product["description"]},
        )
    print(f"✅ Products inserted: {len(PRODUCTS)}")
    return len(PRODUCTS)


# Cypher template lookup for relationship types that point to non-Product nodes
_REL_QUERY_TEMPLATES = {
    "BELONGS_TO": (
        "MATCH (p:Product {name: $src}), (t:Category {name: $tgt}) "
        "MERGE (p)-[:BELONGS_TO]->(t)"
    ),
    "MADE_BY": (
        "MATCH (p:Product {name: $src}), (t:Brand {name: $tgt}) "
        "MERGE (p)-[:MADE_BY]->(t)"
    ),
    "HAS_FEATURE": (
        "MATCH (p:Product {name: $src}), (t:Feature {name: $tgt}) "
        "MERGE (p)-[:HAS_FEATURE]->(t)"
    ),
    "USED_FOR": (
        "MATCH (p:Product {name: $src}), (t:UseCase {name: $tgt}) "
        "MERGE (p)-[:USED_FOR]->(t)"
    ),
}

_PROD_PROD_TEMPLATES = {
    "COMPATIBLE_WITH": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:COMPATIBLE_WITH]->(b)"
    ),
    "ACCESSORY": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:ACCESSORY]->(b)"
    ),
    "WORKS_WITH": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:WORKS_WITH]->(b)"
    ),
    "SIMILAR_TO": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:SIMILAR_TO]->(b)"
    ),
}


def load_relationships(db: Neo4jConnection) -> int:
    """Create all product relationships in the graph."""
    count = 0
    for src, rel_type, tgt in PRODUCT_RELATIONS:
        query = _REL_QUERY_TEMPLATES[rel_type]
        db.run_query(query, {"src": src, "tgt": tgt})
        count += 1

    for src, rel_type, tgt in PRODUCT_PRODUCT_RELATIONS:
        query = _PROD_PROD_TEMPLATES[rel_type]
        db.run_query(query, {"src": src, "tgt": tgt})
        count += 1

    print(f"✅ Relationships created: {count}")
    return count


def load_all(db: Neo4jConnection) -> None:
    """
    Full KG load pipeline.
    Safe to run multiple times (uses MERGE throughout).
    """
    print("\n🚀 Loading ShopGraph Knowledge Graph into Neo4j...\n")
    create_constraints(db)
    load_categories(db)
    load_features(db)
    load_brands(db)
    load_use_cases(db)
    load_products(db)
    load_relationships(db)
    print("\n🎉 Knowledge Graph loaded successfully!\n")
