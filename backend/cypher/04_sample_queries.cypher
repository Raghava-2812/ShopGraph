// ============================================================
// ShopGraph - Sample Queries
// File: 04_sample_queries.cypher
// Useful Cypher queries for exploring the Knowledge Graph
// Run these in Neo4j Browser or Aura Query Editor
// ============================================================

// ── 1. Find a specific product ───────────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"})
RETURN p;

// ── 2. Find product with all its relationships ───────────────
MATCH (p:Product {name: "Dell Inspiron 15"})
OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
OPTIONAL MATCH (p)-[:HAS_FEATURE]->(f:Feature)
OPTIONAL MATCH (p)-[:USED_FOR]->(u:UseCase)
RETURN
  p.name AS product,
  cat.name AS category,
  b.name AS brand,
  collect(DISTINCT f.name) AS features,
  collect(DISTINCT u.name) AS use_cases;

// ── 3. Find direct recommendations (compatible, accessory, etc.) ──
MATCH (p:Product {name: "Dell Inspiron 15"})
-[r:COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO]->
(c:Product)
RETURN c.name AS recommended_product, type(r) AS relationship_type
ORDER BY type(r);

// ── 4. Find products sharing features ────────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"})
-[:HAS_FEATURE]->(f:Feature)
<-[:HAS_FEATURE]-(c:Product)
WHERE c <> p
RETURN
  c.name AS product,
  collect(f.name) AS shared_features,
  count(f) AS feature_overlap_count
ORDER BY feature_overlap_count DESC;

// ── 5. Find products sharing use cases ───────────────────────
MATCH (p:Product {name: "Dell Inspiron 15"})
-[:USED_FOR]->(u:UseCase)
<-[:USED_FOR]-(c:Product)
WHERE c <> p
RETURN
  c.name AS product,
  collect(u.name) AS shared_use_cases,
  count(u) AS use_case_overlap_count
ORDER BY use_case_overlap_count DESC;

// ── 6. Find all candidates for recommendation ────────────────
// Combines all discovery methods
MATCH (p:Product {name: "Dell Inspiron 15"})
OPTIONAL MATCH (p)-[r1:COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO]->(direct:Product)
OPTIONAL MATCH (p)-[:HAS_FEATURE]->(f:Feature)<-[:HAS_FEATURE]-(feature_match:Product)
  WHERE feature_match <> p
OPTIONAL MATCH (p)-[:USED_FOR]->(u:UseCase)<-[:USED_FOR]-(usecase_match:Product)
  WHERE usecase_match <> p
WITH p,
  collect(DISTINCT direct.name) AS direct_matches,
  collect(DISTINCT feature_match.name) AS feature_matches,
  collect(DISTINCT usecase_match.name) AS usecase_matches
RETURN
  direct_matches,
  feature_matches,
  usecase_matches;

// ── 7. Count how many products are in each category ──────────
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
RETURN c.name AS category, count(p) AS product_count
ORDER BY product_count DESC;

// ── 8. Find all Bluetooth products ───────────────────────────
MATCH (p:Product)-[:HAS_FEATURE]->(f:Feature {name: "Bluetooth"})
RETURN p.name AS product, p.price AS price
ORDER BY p.price;

// ── 9. Find products useful for Programming ──────────────────
MATCH (p:Product)-[:USED_FOR]->(u:UseCase {name: "Programming"})
RETURN p.name AS product
ORDER BY p.name;

// ── 10. Find the most connected products ─────────────────────
MATCH (p:Product)-[r]->(n)
WHERE type(r) IN ["COMPATIBLE_WITH", "ACCESSORY", "WORKS_WITH", "SIMILAR_TO"]
RETURN p.name AS product, count(r) AS connection_count
ORDER BY connection_count DESC
LIMIT 10;

// ── 11. Count nodes and relationships ────────────────────────
MATCH (n) RETURN labels(n)[0] AS node_type, count(n) AS count
UNION ALL
MATCH ()-[r]->() RETURN type(r) AS node_type, count(r) AS count;

// ── 12. Show the full knowledge graph path ───────────────────
// Example: How is Dell Inspiron 15 related to Samsung T7 SSD?
MATCH path = (a:Product {name: "Dell Inspiron 15"})
             -[*1..2]->
             (b:Product {name: "Samsung T7 SSD 1TB"})
RETURN path;
