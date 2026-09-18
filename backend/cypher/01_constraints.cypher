// ============================================================
// ShopGraph - Cypher Constraints
// File: 01_constraints.cypher
// Run this FIRST before loading any data
// ============================================================

// Product uniqueness constraint
CREATE CONSTRAINT product_name_unique IF NOT EXISTS
FOR (p:Product)
REQUIRE p.name IS UNIQUE;

// Category uniqueness constraint
CREATE CONSTRAINT category_name_unique IF NOT EXISTS
FOR (c:Category)
REQUIRE c.name IS UNIQUE;

// Feature uniqueness constraint
CREATE CONSTRAINT feature_name_unique IF NOT EXISTS
FOR (f:Feature)
REQUIRE f.name IS UNIQUE;

// Brand uniqueness constraint
CREATE CONSTRAINT brand_name_unique IF NOT EXISTS
FOR (b:Brand)
REQUIRE b.name IS UNIQUE;

// UseCase uniqueness constraint
CREATE CONSTRAINT usecase_name_unique IF NOT EXISTS
FOR (u:UseCase)
REQUIRE u.name IS UNIQUE;
