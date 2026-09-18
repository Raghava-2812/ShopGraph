// ============================================================
// ShopGraph - Create Nodes
// File: 02_create_nodes.cypher
// Creates all Category, Feature, Brand, UseCase, and Product nodes
// Uses MERGE to avoid duplicates - safe to re-run
// ============================================================

// ── Categories ──────────────────────────────────────────────
MERGE (c:Category {name: "Laptop"})          SET c.description = "Portable personal computers";
MERGE (c:Category {name: "Mouse"})           SET c.description = "Pointing input devices";
MERGE (c:Category {name: "Keyboard"})        SET c.description = "Text input devices";
MERGE (c:Category {name: "USB Hub"})         SET c.description = "Multi-port USB connectivity adapters";
MERGE (c:Category {name: "Laptop Stand"})    SET c.description = "Ergonomic stands for laptops";
MERGE (c:Category {name: "Laptop Bag"})      SET c.description = "Carrying cases for laptops";
MERGE (c:Category {name: "Monitor"})         SET c.description = "External display screens";
MERGE (c:Category {name: "Headphones"})      SET c.description = "Personal audio devices";
MERGE (c:Category {name: "Storage"})         SET c.description = "External data storage devices";
MERGE (c:Category {name: "Webcam"})          SET c.description = "Video capture devices for conferencing";

// ── Features ─────────────────────────────────────────────────
MERGE (f:Feature {name: "USB-C"})             SET f.description = "Supports USB Type-C connectivity";
MERGE (f:Feature {name: "Bluetooth"})         SET f.description = "Wireless Bluetooth connectivity";
MERGE (f:Feature {name: "Wireless"})          SET f.description = "Wire-free operation";
MERGE (f:Feature {name: "HDMI"})              SET f.description = "HDMI video output support";
MERGE (f:Feature {name: "WiFi"})              SET f.description = "Built-in wireless internet";
MERGE (f:Feature {name: "Portable"})          SET f.description = "Compact and travel-friendly design";
MERGE (f:Feature {name: "Noise Cancellation"})SET f.description = "Active noise cancellation technology";
MERGE (f:Feature {name: "Mechanical Keys"})   SET f.description = "Mechanical key switches";
MERGE (f:Feature {name: "Ergonomic"})         SET f.description = "Designed for comfort and reduced strain";
MERGE (f:Feature {name: "1TB Storage"})       SET f.description = "One terabyte of storage capacity";

// ── Brands ───────────────────────────────────────────────────
MERGE (b:Brand {name: "Dell"})       SET b.country = "USA";
MERGE (b:Brand {name: "HP"})         SET b.country = "USA";
MERGE (b:Brand {name: "Lenovo"})     SET b.country = "China";
MERGE (b:Brand {name: "Logitech"})   SET b.country = "Switzerland";
MERGE (b:Brand {name: "Keychron"})   SET b.country = "USA";
MERGE (b:Brand {name: "Anker"})      SET b.country = "USA";
MERGE (b:Brand {name: "Sony"})       SET b.country = "Japan";
MERGE (b:Brand {name: "JBL"})        SET b.country = "USA";
MERGE (b:Brand {name: "Samsung"})    SET b.country = "South Korea";
MERGE (b:Brand {name: "LG"})         SET b.country = "South Korea";
MERGE (b:Brand {name: "WD"})         SET b.country = "USA";
MERGE (b:Brand {name: "Portronics"}) SET b.country = "India";

// ── Use Cases ────────────────────────────────────────────────
MERGE (u:UseCase {name: "Programming"})        SET u.description = "Software development and coding work";
MERGE (u:UseCase {name: "Office Work"})        SET u.description = "General office productivity tasks";
MERGE (u:UseCase {name: "Gaming"})             SET u.description = "Video gaming and esports";
MERGE (u:UseCase {name: "Work From Home"})     SET u.description = "Remote work and home office setup";
MERGE (u:UseCase {name: "Entertainment"})      SET u.description = "Media consumption and leisure";
MERGE (u:UseCase {name: "Travel"})             SET u.description = "On-the-go mobile use";
MERGE (u:UseCase {name: "Video Conferencing"}) SET u.description = "Online meetings and video calls";
MERGE (u:UseCase {name: "Content Creation"})   SET u.description = "Digital content production and editing";

// ── Products ─────────────────────────────────────────────────
MERGE (p:Product {name: "Dell Inspiron 15"})
  SET p.price = 55000, p.description = "15-inch laptop suitable for everyday computing and programming";

MERGE (p:Product {name: "HP Pavilion 15"})
  SET p.price = 52000, p.description = "15-inch HP laptop with great performance and battery life";

MERGE (p:Product {name: "Lenovo IdeaPad Slim 5"})
  SET p.price = 57000, p.description = "Slim 15-inch laptop with excellent keyboard and display";

MERGE (p:Product {name: "Logitech MX Master 3S"})
  SET p.price = 9000, p.description = "Advanced wireless ergonomic mouse for professionals";

MERGE (p:Product {name: "Logitech M331"})
  SET p.price = 2500, p.description = "Silent wireless mouse for everyday use";

MERGE (p:Product {name: "Keychron K2"})
  SET p.price = 7500, p.description = "Compact mechanical keyboard with Bluetooth and hot-swap support";

MERGE (p:Product {name: "Logitech K380"})
  SET p.price = 3500, p.description = "Compact multi-device Bluetooth keyboard";

MERGE (p:Product {name: "Dell USB-C Hub"})
  SET p.price = 4500, p.description = "7-in-1 USB-C hub with HDMI and USB ports";

MERGE (p:Product {name: "Anker USB-C Hub"})
  SET p.price = 3500, p.description = "Compact 6-in-1 USB-C hub with power delivery";

MERGE (p:Product {name: "Dell Laptop Stand"})
  SET p.price = 3000, p.description = "Adjustable aluminum laptop stand for ergonomic setup";

MERGE (p:Product {name: "Portronics Laptop Stand"})
  SET p.price = 1500, p.description = "Portable foldable laptop stand for desk or travel";

MERGE (p:Product {name: "Dell Laptop Bag"})
  SET p.price = 2500, p.description = "Durable 15-inch laptop bag with multiple compartments";

MERGE (p:Product {name: "HP Laptop Backpack"})
  SET p.price = 2000, p.description = "Water-resistant 15.6-inch laptop backpack";

MERGE (p:Product {name: "LG 24 inch Monitor"})
  SET p.price = 15000, p.description = "24-inch IPS FHD monitor with USB-C and HDMI";

MERGE (p:Product {name: "Dell 24 inch Monitor"})
  SET p.price = 16000, p.description = "24-inch IPS monitor with anti-glare screen and HDMI";

MERGE (p:Product {name: "Sony WH-1000XM5"})
  SET p.price = 29000, p.description = "Industry-leading noise cancelling wireless headphones";

MERGE (p:Product {name: "JBL Tune 770NC"})
  SET p.price = 8000, p.description = "Adaptive noise cancelling wireless headphones";

MERGE (p:Product {name: "Samsung T7 SSD 1TB"})
  SET p.price = 8500, p.description = "Portable SSD with USB-C and fast transfer speeds";

MERGE (p:Product {name: "WD My Passport 1TB"})
  SET p.price = 4500, p.description = "Compact USB-C portable hard drive";

MERGE (p:Product {name: "Logitech C920 Webcam"})
  SET p.price = 7000, p.description = "Full HD 1080p webcam for video conferencing";
