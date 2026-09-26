"""
ShopGraph - In-Memory Knowledge Graph Fallback
app/mock_kg.py

Provides a high-performance in-memory graph representation of the ShopGraph
Knowledge Graph. Used automatically when Neo4j is offline, unreachable, or
during local development/testing without an active Neo4j instance.
"""

from typing import Any
from app.kg_loader import (
    PRODUCTS,
    CATEGORIES,
    FEATURES,
    BRANDS,
    USE_CASES,
    PRODUCT_RELATIONS,
    PRODUCT_PRODUCT_RELATIONS,
)


class InMemoryKnowledgeGraph:
    """In-memory Knowledge Graph that evaluates ShopGraph Cypher queries."""

    def __init__(self):
        # Index products by name with a full shallow copy
        self.products = {}
        for p in PRODUCTS:
            prod_copy = dict(p)
            prod_copy["features"] = set(p.get("features", []))
            prod_copy["use_cases"] = set(p.get("use_cases", []))
            prod_copy["compatible_with"] = set()
            prod_copy["accessories"] = set()
            prod_copy["works_with"] = set()
            prod_copy["similar_to"] = set()
            self.products[p["name"]] = prod_copy

        self.categories = {c["name"]: dict(c) for c in CATEGORIES}
        self.features = {f["name"]: dict(f) for f in FEATURES}
        self.brands = {b["name"]: dict(b) for b in BRANDS}
        self.use_cases = {u["name"]: dict(u) for u in USE_CASES}

        # Load entity relationships
        for src, rel, tgt in PRODUCT_RELATIONS:
            if src in self.products:
                if rel == "BELONGS_TO":
                    self.products[src]["category"] = tgt
                elif rel == "MADE_BY":
                    self.products[src]["brand"] = tgt
                elif rel == "HAS_FEATURE":
                    self.products[src]["features"].add(tgt)
                elif rel == "USED_FOR":
                    self.products[src]["use_cases"].add(tgt)

        # Load product-to-product relationships
        for src, rel, tgt in PRODUCT_PRODUCT_RELATIONS:
            if src in self.products:
                if rel == "COMPATIBLE_WITH":
                    self.products[src]["compatible_with"].add(tgt)
                elif rel == "ACCESSORY":
                    self.products[src]["accessories"].add(tgt)
                elif rel == "WORKS_WITH":
                    self.products[src]["works_with"].add(tgt)
                elif rel == "SIMILAR_TO":
                    self.products[src]["similar_to"].add(tgt)

    def _format_product(self, p: dict) -> dict:
        """Format product record with all rich e-commerce attributes."""
        return {
            "name": p.get("name"),
            "slug": p.get("slug", ""),
            "price": p.get("price"),
            "original_price": p.get("original_price", p.get("price")),
            "discount_percentage": p.get("discount_percentage", 0),
            "rating": p.get("rating", 4.5),
            "review_count": p.get("review_count", 100),
            "stock": p.get("stock", 25),
            "image_url": p.get("image_url", ""),
            "description": p.get("description", ""),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "model": p.get("model", ""),
            "release_year": p.get("release_year", 2023),
            "specs": p.get("specs", {}),
        }

    def run_query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Interpret and execute Cypher query against in-memory graph."""
        params = parameters or {}
        q = query.strip()

        # 1. Count query
        if "count(n)" in q or "count(p)" in q:
            return [{"count": len(self.products)}]

        # 2. List categories
        if "MATCH (c:Category)" in q:
            cats = sorted(self.categories.keys())
            return [{"name": c} for c in cats]

        # 3. Product details (full view with relations and specs)
        if "collect(DISTINCT comp.name)" in q or "collect(DISTINCT acc.name)" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return [{"name": None}]
            rec = self._format_product(p)
            rec.update({
                "features": sorted(list(p["features"])),
                "use_cases": sorted(list(p["use_cases"])),
                "compatible_with": sorted(list(p["compatible_with"])),
                "accessories": sorted(list(p["accessories"])),
                "works_with": sorted(list(p["works_with"])),
                "similar_to": sorted(list(p["similar_to"])),
            })
            return [rec]

        # 4. Recommender product info
        if "collect(DISTINCT f.name)" in q and "cat.name AS category" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return [{"name": None}]
            return [{
                "name": p["name"],
                "features": sorted(list(p["features"])),
                "use_cases": sorted(list(p["use_cases"])),
                "category": p["category"],
                "brand": p["brand"],
            }]

        # 5. Direct candidates (COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO)
        if "COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            results = []
            for c in sorted(p["compatible_with"]):
                results.append({"candidate": c, "rel_type": "COMPATIBLE_WITH"})
            for a in sorted(p["accessories"]):
                results.append({"candidate": a, "rel_type": "ACCESSORY"})
            for w in sorted(p["works_with"]):
                results.append({"candidate": w, "rel_type": "WORKS_WITH"})
            for s in sorted(p["similar_to"]):
                results.append({"candidate": s, "rel_type": "SIMILAR_TO"})
            return results

        # 6. Feature candidates
        if "[:HAS_FEATURE]->(f:Feature)<-[:HAS_FEATURE]" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            src_features = p["features"]
            results = []
            for other_name, other_p in sorted(self.products.items()):
                if other_name == name:
                    continue
                shared = sorted(list(src_features & other_p["features"]))
                if shared:
                    results.append({"candidate": other_name, "shared_features": shared})
            return results

        # 7. Use case candidates
        if "[:USED_FOR]->(u:UseCase)<-[:USED_FOR]" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            src_use_cases = p["use_cases"]
            results = []
            for other_name, other_p in sorted(self.products.items()):
                if other_name == name:
                    continue
                shared = sorted(list(src_use_cases & other_p["use_cases"]))
                if shared:
                    results.append({"candidate": other_name, "shared_use_cases": shared})
            return results

        # 8. Same category candidates
        if "[:BELONGS_TO]->(cat:Category)<-[:BELONGS_TO]" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p or not p["category"]:
                return []
            cat = p["category"]
            results = []
            for other_name, other_p in sorted(self.products.items()):
                if other_name != name and other_p["category"] == cat:
                    results.append({"candidate": other_name})
            return results

        # 9. Recommendations sections queries
        if "-[:COMPATIBLE_WITH|WORKS_WITH]->" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            compat = p["compatible_with"] | p["works_with"]
            return [{"name": c} for c in sorted(compat)]

        if "-[:ACCESSORY]->" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            return [{"name": a} for a in sorted(p["accessories"])]

        if "-[:SIMILAR_TO]->" in q:
            name = params.get("name")
            p = self.products.get(name)
            if not p:
                return []
            return [{"name": s} for s in sorted(p["similar_to"])]

        # 10. Category lookup queries
        if "WHERE p.name IN $names" in q and "c.name AS category" in q:
            names = params.get("names", [])
            categories = set()
            for n in names:
                if n in self.products and self.products[n]["category"]:
                    categories.add(self.products[n]["category"])
            return [{"category": c} for c in sorted(categories)]

        if "MATCH (p:Product {name: $name})-[:BELONGS_TO]->(c:Category)" in q:
            name = params.get("name")
            p = self.products.get(name)
            if p and p["category"]:
                return [{"category": p["category"]}]
            return []

        # 11. Search query
        if "WHERE toLower(p.name) CONTAINS toLower($q)" in q or "CONTAINS toLower($q)" in q:
            search_term = str(params.get("q", "")).lower()
            results = []
            for p in sorted(self.products.values(), key=lambda x: x["name"]):
                name_match = search_term in p["name"].lower()
                desc_match = search_term in (p.get("description") or "").lower()
                cat_match = search_term in (p.get("category") or "").lower()
                brand_match = search_term in (p.get("brand") or "").lower()
                if name_match or desc_match or cat_match or brand_match:
                    results.append(self._format_product(p))
            return results

        # 12. Filter by names (WHERE p.name IN $names)
        if "WHERE p.name IN $names" in q:
            names = params.get("names", [])
            results = []
            for name in names:
                if name in self.products:
                    results.append(self._format_product(self.products[name]))
            return results

        # 13. General List products (with optional category, brand, or limit)
        if "MATCH (p:Product)" in q:
            category = params.get("category")
            brand = params.get("brand")
            limit = params.get("limit")
            results = []
            for p in sorted(self.products.values(), key=lambda x: (x.get("category") or "", x["name"])):
                if category and p.get("category") != category:
                    continue
                if brand and p.get("brand") != brand:
                    continue
                results.append(self._format_product(p))
            if limit is not None:
                results = results[:int(limit)]
            return results

        # Default fallback for unhandled DDL/schema queries
        return []


# Global in-memory KG instance
mock_kg = InMemoryKnowledgeGraph()
