// ============================================================
// ShopGraph - Graph Visualization Queries
// File: 05_visualization.cypher
// Run these in Neo4j Browser for visual graph exploration
// ============================================================

// ── Full graph (limited) ─────────────────────────────────────
// Paste this in Neo4j Browser to see the entire knowledge graph
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 100;

// ── Product neighborhood for Dell Inspiron 15 ───────────────
MATCH (p:Product {name: "Dell Inspiron 15"})-[r]->(n)
RETURN p, r, n;

// ── All product-to-product relationships ─────────────────────
MATCH (a:Product)-[r:COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO]->(b:Product)
RETURN a, r, b;

// ── Product features subgraph ────────────────────────────────
MATCH (p:Product)-[r:HAS_FEATURE]->(f:Feature)
RETURN p, r, f;

// ── Product use case subgraph ────────────────────────────────
MATCH (p:Product)-[r:USED_FOR]->(u:UseCase)
RETURN p, r, u;

// ── Brand ecosystem ──────────────────────────────────────────
MATCH (p:Product)-[r:MADE_BY]->(b:Brand)
RETURN p, r, b;
