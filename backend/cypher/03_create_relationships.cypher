// ============================================================
// ShopGraph - Create Relationships
// File: 03_create_relationships.cypher
// Creates all edges in the knowledge graph
// Uses MERGE to avoid duplicate relationships
// ============================================================

// ── BELONGS_TO (Product → Category) ─────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"}),     (c:Category {name: "Laptop"})       MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "HP Pavilion 15"}),        (c:Category {name: "Laptop"})       MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}), (c:Category {name: "Laptop"})       MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Logitech MX Master 3S"}), (c:Category {name: "Mouse"})        MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Logitech M331"}),         (c:Category {name: "Mouse"})        MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Keychron K2"}),           (c:Category {name: "Keyboard"})     MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Logitech K380"}),         (c:Category {name: "Keyboard"})     MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Dell USB-C Hub"}),        (c:Category {name: "USB Hub"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Anker USB-C Hub"}),       (c:Category {name: "USB Hub"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Dell Laptop Stand"}),     (c:Category {name: "Laptop Stand"}) MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(c:Category {name: "Laptop Stand"})MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Dell Laptop Bag"}),       (c:Category {name: "Laptop Bag"})   MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "HP Laptop Backpack"}),    (c:Category {name: "Laptop Bag"})   MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "LG 24 inch Monitor"}),    (c:Category {name: "Monitor"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),  (c:Category {name: "Monitor"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Sony WH-1000XM5"}),       (c:Category {name: "Headphones"})   MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "JBL Tune 770NC"}),        (c:Category {name: "Headphones"})   MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),    (c:Category {name: "Storage"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "WD My Passport 1TB"}),    (c:Category {name: "Storage"})      MERGE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {name: "Logitech C920 Webcam"}),  (c:Category {name: "Webcam"})       MERGE (p)-[:BELONGS_TO]->(c);

// ── MADE_BY (Product → Brand) ────────────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"}),      (b:Brand {name: "Dell"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "HP Pavilion 15"}),         (b:Brand {name: "HP"})        MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (b:Brand {name: "Lenovo"})    MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (b:Brand {name: "Logitech"})  MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Logitech M331"}),          (b:Brand {name: "Logitech"})  MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Keychron K2"}),            (b:Brand {name: "Keychron"})  MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Logitech K380"}),          (b:Brand {name: "Logitech"})  MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Dell USB-C Hub"}),         (b:Brand {name: "Dell"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (b:Brand {name: "Anker"})     MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Dell Laptop Stand"}),      (b:Brand {name: "Dell"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(b:Brand {name: "Portronics"})MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Dell Laptop Bag"}),        (b:Brand {name: "Dell"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "HP Laptop Backpack"}),     (b:Brand {name: "HP"})        MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (b:Brand {name: "LG"})        MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),   (b:Brand {name: "Dell"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (b:Brand {name: "Sony"})      MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (b:Brand {name: "JBL"})       MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (b:Brand {name: "Samsung"})   MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (b:Brand {name: "WD"})        MERGE (p)-[:MADE_BY]->(b);
MATCH (p:Product {name: "Logitech C920 Webcam"}),   (b:Brand {name: "Logitech"})  MERGE (p)-[:MADE_BY]->(b);

// ── HAS_FEATURE (Product → Feature) ─────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"}),      (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell Inspiron 15"}),      (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell Inspiron 15"}),      (f:Feature {name: "WiFi"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "HP Pavilion 15"}),         (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "HP Pavilion 15"}),         (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "HP Pavilion 15"}),         (f:Feature {name: "WiFi"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (f:Feature {name: "WiFi"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (f:Feature {name: "Ergonomic"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech M331"}),          (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech M331"}),          (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Keychron K2"}),            (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Keychron K2"}),            (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Keychron K2"}),            (f:Feature {name: "Mechanical Keys"})  MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech K380"}),          (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech K380"}),          (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech K380"}),          (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell USB-C Hub"}),         (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell USB-C Hub"}),         (f:Feature {name: "HDMI"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (f:Feature {name: "HDMI"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell Laptop Stand"}),      (f:Feature {name: "Ergonomic"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(f:Feature {name: "Ergonomic"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (f:Feature {name: "HDMI"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),   (f:Feature {name: "HDMI"})             MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (f:Feature {name: "Noise Cancellation"})MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (f:Feature {name: "Bluetooth"})        MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (f:Feature {name: "Wireless"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (f:Feature {name: "Noise Cancellation"})MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (f:Feature {name: "1TB Storage"})      MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (f:Feature {name: "USB-C"})           MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (f:Feature {name: "1TB Storage"})      MERGE (p)-[:HAS_FEATURE]->(f);
MATCH (p:Product {name: "Logitech C920 Webcam"}),   (f:Feature {name: "Portable"})         MERGE (p)-[:HAS_FEATURE]->(f);

// ── USED_FOR (Product → UseCase) ─────────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"}),      (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell Inspiron 15"}),      (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell Inspiron 15"}),      (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "HP Pavilion 15"}),         (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "HP Pavilion 15"}),         (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "HP Pavilion 15"}),         (u:UseCase {name: "Entertainment"})       MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Lenovo IdeaPad Slim 5"}),  (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech MX Master 3S"}),  (u:UseCase {name: "Content Creation"})    MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech M331"}),          (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech M331"}),          (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Keychron K2"}),            (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Keychron K2"}),            (u:UseCase {name: "Gaming"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Keychron K2"}),            (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech K380"}),          (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech K380"}),          (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech K380"}),          (u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell USB-C Hub"}),         (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell USB-C Hub"}),         (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Anker USB-C Hub"}),        (u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell Laptop Stand"}),      (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell Laptop Stand"}),      (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Portronics Laptop Stand"}),(u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "LG 24 inch Monitor"}),     (u:UseCase {name: "Gaming"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),   (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),   (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Dell 24 inch Monitor"}),   (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (u:UseCase {name: "Entertainment"})       MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Sony WH-1000XM5"}),        (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (u:UseCase {name: "Entertainment"})       MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "JBL Tune 770NC"}),         (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (u:UseCase {name: "Programming"})        MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Samsung T7 SSD 1TB"}),     (u:UseCase {name: "Content Creation"})    MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (u:UseCase {name: "Office Work"})         MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "WD My Passport 1TB"}),     (u:UseCase {name: "Travel"})              MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech C920 Webcam"}),   (u:UseCase {name: "Video Conferencing"})  MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech C920 Webcam"}),   (u:UseCase {name: "Content Creation"})    MERGE (p)-[:USED_FOR]->(u);
MATCH (p:Product {name: "Logitech C920 Webcam"}),   (u:UseCase {name: "Work From Home"})      MERGE (p)-[:USED_FOR]->(u);

// ── COMPATIBLE_WITH (Product ↔ Product) ──────────────────────
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Logitech MX Master 3S"}) MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Logitech M331"})          MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Keychron K2"})            MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Logitech K380"})          MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Dell USB-C Hub"})         MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Anker USB-C Hub"})        MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Samsung T7 SSD 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "WD My Passport 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Logitech MX Master 3S"}) MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Logitech M331"})          MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Keychron K2"})            MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Logitech K380"})          MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Anker USB-C Hub"})        MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Samsung T7 SSD 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "WD My Passport 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Logitech MX Master 3S"}) MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Keychron K2"})            MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Logitech K380"})          MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Anker USB-C Hub"})        MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Samsung T7 SSD 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "WD My Passport 1TB"})     MERGE (a)-[:COMPATIBLE_WITH]->(b);

// ── ACCESSORY (Product → Product) ───────────────────────────
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Dell Laptop Stand"})      MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Portronics Laptop Stand"}) MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Dell Laptop Bag"})         MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "HP Laptop Backpack"})      MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Portronics Laptop Stand"}) MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "HP Laptop Backpack"})      MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Portronics Laptop Stand"}) MERGE (a)-[:ACCESSORY]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Dell Laptop Bag"})         MERGE (a)-[:ACCESSORY]->(b);

// ── WORKS_WITH (Product → Product) ──────────────────────────
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Dell 24 inch Monitor"})  MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "LG 24 inch Monitor"})    MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),     (b:Product {name: "Logitech C920 Webcam"})  MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "LG 24 inch Monitor"})    MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),        (b:Product {name: "Logitech C920 Webcam"})  MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "LG 24 inch Monitor"})    MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Dell 24 inch Monitor"})  MERGE (a)-[:WORKS_WITH]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}), (b:Product {name: "Logitech C920 Webcam"})  MERGE (a)-[:WORKS_WITH]->(b);

// ── SIMILAR_TO (Product ↔ Product) ──────────────────────────
MATCH (a:Product {name: "Dell Inspiron 15"}),      (b:Product {name: "HP Pavilion 15"})           MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Dell Inspiron 15"}),      (b:Product {name: "Lenovo IdeaPad Slim 5"})    MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),         (b:Product {name: "Dell Inspiron 15"})         MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "HP Pavilion 15"}),         (b:Product {name: "Lenovo IdeaPad Slim 5"})    MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}),  (b:Product {name: "Dell Inspiron 15"})         MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Lenovo IdeaPad Slim 5"}),  (b:Product {name: "HP Pavilion 15"})           MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Logitech MX Master 3S"}),  (b:Product {name: "Logitech M331"})            MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Logitech M331"}),          (b:Product {name: "Logitech MX Master 3S"})    MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Keychron K2"}),            (b:Product {name: "Logitech K380"})            MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Logitech K380"}),          (b:Product {name: "Keychron K2"})              MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Dell USB-C Hub"}),         (b:Product {name: "Anker USB-C Hub"})          MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Anker USB-C Hub"}),        (b:Product {name: "Dell USB-C Hub"})           MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Dell Laptop Stand"}),      (b:Product {name: "Portronics Laptop Stand"})  MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Portronics Laptop Stand"}),(b:Product {name: "Dell Laptop Stand"})        MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "LG 24 inch Monitor"}),     (b:Product {name: "Dell 24 inch Monitor"})     MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Dell 24 inch Monitor"}),   (b:Product {name: "LG 24 inch Monitor"})       MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Sony WH-1000XM5"}),        (b:Product {name: "JBL Tune 770NC"})           MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "JBL Tune 770NC"}),         (b:Product {name: "Sony WH-1000XM5"})          MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "Samsung T7 SSD 1TB"}),     (b:Product {name: "WD My Passport 1TB"})       MERGE (a)-[:SIMILAR_TO]->(b);
MATCH (a:Product {name: "WD My Passport 1TB"}),     (b:Product {name: "Samsung T7 SSD 1TB"})       MERGE (a)-[:SIMILAR_TO]->(b);
