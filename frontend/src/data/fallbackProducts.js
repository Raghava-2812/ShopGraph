/**
 * Fallback product list.
 * 
 * NOTE: This is strictly used as an offline/development fallback if the
 * FastAPI backend (/products) cannot be reached. In normal operation,
 * products are fetched dynamically from the Neo4j Knowledge Graph.
 */
export const FALLBACK_PRODUCTS = [
  "Dell Inspiron 15",
  "HP Pavilion 15",
  "Lenovo IdeaPad Slim 5",
  "Logitech MX Master 3S",
  "Logitech M331",
  "Keychron K2",
  "Logitech K380",
  "Dell USB-C Hub",
  "Anker USB-C Hub",
  "Dell Laptop Stand",
  "Portronics Laptop Stand",
  "Dell Laptop Bag",
  "HP Laptop Backpack",
  "LG 24 inch Monitor",
  "Dell 24 inch Monitor",
  "Sony WH-1000XM5",
  "JBL Tune 770NC",
  "Samsung T7 SSD 1TB",
  "WD My Passport 1TB",
  "Logitech C920 Webcam"
];
