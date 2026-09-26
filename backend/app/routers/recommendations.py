"""
ShopGraph - Recommendations Router
app/routers/recommendations.py

Routes:
  GET /recommendations                                - Personalized for logged-in user / Home page
  GET /recommendations/product/{name}                 - Product-context recommendations
  GET /recommendations/cart                           - Cart-based recommendations ("Complete Your Setup")
  GET /recommendations/recently-viewed                - User's recently viewed products
  GET /recommendations/category/{category_name}       - Category top picks + accessories

Scoring formula (transparent, explainable, no ML):
  Final Score = (
      relationship_score  * settings.WEIGHT_RELATIONSHIP   (0.30)
    + feature_score       * settings.WEIGHT_FEATURE        (0.20)
    + category_score      * settings.WEIGHT_CATEGORY       (0.15)
    + use_case_score      * settings.WEIGHT_USE_CASE       (0.10)
    + user_interest_score * settings.WEIGHT_USER_INTEREST  (0.15)
    + popularity_score    * settings.WEIGHT_POPULARITY     (0.05)
    + recency_score       * settings.WEIGHT_RECENCY        (0.05)
  ) * 100
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from collections import Counter

from app.config import settings
from app.sqlite_db import get_sqlite_db, UserEvent, CartItem, Cart, WishlistItem, User
from app.auth import get_optional_user
from app.database import get_db
from app.candidate_generator import CandidateGenerator, CandidateInfo
from app.explanation import generate_reasons

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


# ── User Behavior Helper ──────────────────────────────────────────────────────

def get_user_behavior(user_id: int, db: Session, days: int = 30) -> dict:
    """Fetch user behavior signals from SQLite within the last `days` days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    events = db.query(UserEvent).filter(
        UserEvent.user_id == user_id,
        UserEvent.created_at >= since,
    ).order_by(UserEvent.created_at.desc()).all()

    behavior = {
        "viewed": [],
        "viewed_categories": [],
        "searched": [],
        "carted": [],
        "purchased": [],
        "wishlisted": [],
    }

    seen_views = set()
    for e in events:
        if e.event_type in ("VIEW", "VIEW_PRODUCT") and e.product_name:
            if e.product_name not in seen_views:
                behavior["viewed"].append(e.product_name)
                seen_views.add(e.product_name)
            if e.category_name:
                behavior["viewed_categories"].append(e.category_name)
        elif e.event_type in ("SEARCH", "SEARCH_PRODUCT") and e.search_query:
            behavior["searched"].append(e.search_query)
        elif e.event_type in ("ADD_TO_CART",) and e.product_name:
            behavior["carted"].append(e.product_name)
        elif e.event_type in ("PURCHASE", "PURCHASE_PRODUCT") and e.product_name:
            behavior["purchased"].append(e.product_name)
        elif e.event_type in ("WISHLIST", "WISHLIST_PRODUCT") and e.product_name:
            behavior["wishlisted"].append(e.product_name)

    # Also fetch currently wishlisted items from WishlistItem table
    wish_items = db.query(WishlistItem).filter(WishlistItem.user_id == user_id).all()
    for w in wish_items:
        if w.product_name not in behavior["wishlisted"]:
            behavior["wishlisted"].append(w.product_name)

    return behavior


# ── Product Info Batch Enrichment ─────────────────────────────────────────────

def enrich_products_info(product_names: list[str], neo4j_db) -> dict[str, dict]:
    """Fetch full rich product data from the Knowledge Graph for a list of names."""
    if not product_names:
        return {}
    query = """
    MATCH (p:Product)
    WHERE p.name IN $names
    RETURN p.name AS name, p.price AS price, p.original_price AS original_price,
           p.discount_percentage AS discount_percentage, p.description AS description,
           p.rating AS rating, p.review_count AS review_count, p.stock AS stock,
           p.image_url AS image_url, p.category AS category, p.brand AS brand,
           p.slug AS slug, p.specs AS specs
    """
    rows = neo4j_db.run_query(query, {"names": product_names})
    return {r["name"]: r for r in rows}


# ── Scoring Function ──────────────────────────────────────────────────────────

def calculate_transparent_score(
    candidate_name: str,
    candidate_info: Optional[CandidateInfo],
    candidate_data: dict,
    context_product_data: Optional[dict],
    user_behavior: Optional[dict],
) -> tuple[float, list[str]]:
    """
    Calculate 7-dimension transparent score based on graph signals and user behavior.
    """
    reasons = []

    # 1. Relationship Score (0.0 to 1.0)
    rel_weights = {
        "COMPATIBLE_WITH": 1.0,
        "ACCESSORY": 1.0,
        "WORKS_WITH": 0.9,
        "SIMILAR_TO": 0.7,
    }
    rel_score = 0.0
    if candidate_info and candidate_info.direct_relationships:
        rel_score = max(rel_weights.get(r, 0.4) for r in candidate_info.direct_relationships)
        for r in candidate_info.direct_relationships:
            if r == "COMPATIBLE_WITH":
                reasons.append(f"Directly compatible with {context_product_data.get('name', 'selected product')}")
            elif r == "ACCESSORY":
                reasons.append(f"Recommended accessory for {context_product_data.get('name', 'selected product')}")
            elif r == "WORKS_WITH":
                reasons.append(f"Works seamlessly with {context_product_data.get('name', 'selected product')}")
            elif r == "SIMILAR_TO":
                reasons.append(f"Popular alternative to {context_product_data.get('name', 'selected product')}")

    # 2. Feature Score (0.0 to 1.0)
    feat_score = 0.0
    if candidate_info and candidate_info.shared_features:
        feat_score = min(len(candidate_info.shared_features) / 4.0, 1.0)
        reasons.append(f"Shares features: {', '.join(candidate_info.shared_features[:2])}")

    # 3. Category Score (0.0 to 1.0)
    cat_score = 0.0
    cand_cat = candidate_data.get("category")
    if context_product_data and cand_cat and cand_cat == context_product_data.get("category"):
        cat_score = 0.8
        if not candidate_info or not candidate_info.direct_relationships:
            reasons.append(f"Also in {cand_cat}")

    # 4. Use Case Score (0.0 to 1.0)
    use_case_score = 0.0
    if candidate_info and candidate_info.shared_use_cases:
        use_case_score = min(len(candidate_info.shared_use_cases) / 3.0, 1.0)
        reasons.append(f"Great for {', '.join(candidate_info.shared_use_cases[:2])}")

    # 5. User Interest Score (0.0 to 1.0)
    user_interest_score = 0.0
    if user_behavior:
        # Check category affinity
        top_cats = user_behavior.get("top_categories", [])
        if cand_cat and cand_cat in top_cats:
            user_interest_score += 0.5
            reasons.append(f"Matches your interest in {cand_cat}")

        # Check search match
        for q in user_behavior.get("searched", []):
            if q.lower() in candidate_name.lower():
                user_interest_score += 0.4
                reasons.append(f"Matches your recent search for '{q}'")
                break

        # Check wishlist bonus
        if candidate_name in user_behavior.get("wishlisted", []):
            user_interest_score += 0.6
            reasons.append("Saved in your wishlist")

        user_interest_score = min(user_interest_score, 1.0)

    # 6. Popularity Score (0.0 to 1.0) based on rating & review count
    rating = float(candidate_data.get("rating") or 4.0)
    reviews = int(candidate_data.get("review_count") or 50)
    pop_score = min(((rating / 5.0) * 0.7 + min(reviews / 1000.0, 1.0) * 0.3), 1.0)

    # 7. Recency Score (0.0 to 1.0)
    recency_score = 0.7  # default high baseline for curated catalog

    # Compute Weighted Final Score
    raw_score = (
        rel_score * settings.WEIGHT_RELATIONSHIP
        + feat_score * settings.WEIGHT_FEATURE
        + cat_score * settings.WEIGHT_CATEGORY
        + use_case_score * settings.WEIGHT_USE_CASE
        + user_interest_score * settings.WEIGHT_USER_INTEREST
        + pop_score * settings.WEIGHT_POPULARITY
        + recency_score * settings.WEIGHT_RECENCY
    ) * 100.0

    final_score = min(round(raw_score, 1), 99.5)
    if not reasons:
        reasons.append("Highly rated customer favorite")

    # Deduplicate reasons while preserving order
    seen_reasons = set()
    deduped_reasons = []
    for r in reasons:
        if r not in seen_reasons:
            deduped_reasons.append(r)
            seen_reasons.add(r)

    return final_score, deduped_reasons


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/product/{product_name}")
def recommend_for_product(
    product_name: str,
    top_k: int = Query(default=6, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Dynamic product-page recommendations divided into clearly distinct sections:
      - Related Products (product-centric: same category, brand, features, alternatives)
      - Recommended Products (user + context-centric)
      - Because You Viewed [Current Product] (dynamic category alternatives)
      - Compatible With (graph relationships)
      - Recommended Accessories (graph relationships)
    """
    with get_db() as neo4j_db:
        # 1. Fetch current product data
        prod_rows = neo4j_db.run_query(
            "MATCH (p:Product {name: $name}) RETURN p.name AS name, p.category AS category, p.brand AS brand",
            {"name": product_name},
        )
        if not prod_rows:
            raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
        current_prod = prod_rows[0]

        # 2. Candidate generation via Graph traversal
        generator = CandidateGenerator(neo4j_db)
        candidates = generator.generate_candidates(product_name)

        # 3. User behavior signals
        behavior = None
        purchased_set = set()
        if current_user:
            behavior = get_user_behavior(current_user.id, db)
            purchased_set = set(behavior.get("purchased", []))
            # Calculate top categories
            cat_counts = Counter(behavior.get("viewed_categories", []))
            behavior["top_categories"] = [c for c, _ in cat_counts.most_common(3)]

        # Fetch product details for all candidates
        cand_names = [name for name in candidates.keys() if name != product_name and name not in purchased_set]
        info_map = enrich_products_info(cand_names, neo4j_db)

        # Score candidates
        scored_recs = []
        for name, cinfo in candidates.items():
            if name == product_name or name in purchased_set or name not in info_map:
                continue
            cand_data = info_map[name]
            score, reasons = calculate_transparent_score(
                candidate_name=name,
                candidate_info=cinfo,
                candidate_data=cand_data,
                context_product_data=current_prod,
                user_behavior=behavior,
            )
            scored_recs.append({
                "product": name,
                "score": score,
                "reasons": reasons,
                "product_info": cand_data,
                "candidate_info": cinfo,
            })

        scored_recs.sort(key=lambda r: r["score"], reverse=True)

        # 4. Partition into distinctive sections
        # A. Compatible Products
        compat_rows = neo4j_db.run_query(
            "MATCH (p:Product {name: $name})-[:COMPATIBLE_WITH|WORKS_WITH]->(c:Product) RETURN c.name AS name",
            {"name": product_name},
        )
        compat_names = {r["name"] for r in compat_rows}
        compatible_with = [r for r in scored_recs if r["product"] in compat_names][:top_k]

        # B. Recommended Accessories
        acc_rows = neo4j_db.run_query(
            "MATCH (p:Product {name: $name})-[:ACCESSORY]->(c:Product) RETURN c.name AS name",
            {"name": product_name},
        )
        acc_names = {r["name"] for r in acc_rows}
        accessories = [r for r in scored_recs if r["product"] in acc_names][:top_k]

        # C. Related Products (product-centric: same category, brand, or SIMILAR_TO)
        current_cat = current_prod.get("category")
        current_brand = current_prod.get("brand")
        related = [
            r for r in scored_recs
            if r["product"] not in compat_names
            and r["product"] not in acc_names
            and (
                r["product_info"].get("category") == current_cat
                or r["product_info"].get("brand") == current_brand
                or "SIMILAR_TO" in r["candidate_info"].direct_relationships
            )
        ][:top_k]

        # D. Because You Viewed [Current Product] (alternatives with dynamic title)
        because_you_viewed = [
            r for r in scored_recs
            if r["product_info"].get("category") == current_cat
            and r["product"] != product_name
        ][:top_k]

        # E. Recommended For You (overall top personalized candidates)
        recommended_for_you = scored_recs[:top_k]

    return {
        "context_product": product_name,
        "category": current_prod.get("category"),
        "related_products": related,
        "recommended_for_you": recommended_for_you,
        "because_you_viewed": {
            "title": f"Because You Viewed {product_name}",
            "products": because_you_viewed,
        },
        "compatible_with": compatible_with,
        "accessories": accessories,
        # Backward compatibility with existing frontend
        "sections": {
            "you_may_also_like": related,
            "compatible_with": compatible_with,
            "accessories": accessories,
        },
        "recommendations": recommended_for_you,
    }


@router.get("/recently-viewed")
def get_recently_viewed(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
    limit: int = Query(default=8, ge=1, le=20),
):
    """Return recently viewed products for the authenticated user."""
    if not current_user:
        return {"items": []}

    events = db.query(UserEvent).filter(
        UserEvent.user_id == current_user.id,
        UserEvent.event_type.in_(("VIEW", "VIEW_PRODUCT")),
        UserEvent.product_name.isnot(None),
    ).order_by(UserEvent.created_at.desc()).all()

    seen = set()
    recent_names = []
    for e in events:
        if e.product_name not in seen:
            seen.add(e.product_name)
            recent_names.append(e.product_name)
        if len(recent_names) >= limit:
            break

    if not recent_names:
        return {"items": []}

    with get_db() as neo4j_db:
        info_map = enrich_products_info(recent_names, neo4j_db)

    items = [info_map[name] for name in recent_names if name in info_map]
    return {"items": items}


@router.get("/cart")
def recommend_for_cart(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Get 'Complete Your Setup' recommendations based on all products in user's cart
    using Knowledge Graph ACCESSORY and COMPATIBLE_WITH traversals.
    """
    if not current_user:
        return {"recommendations": [], "message": "Login to see personalized setup recommendations"}

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return {"recommendations": []}

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        return {"recommendations": []}

    cart_product_names = [item.product_name for item in cart_items]
    cart_product_set = set(cart_product_names)

    all_candidates: dict[str, dict] = {}
    with get_db() as neo4j_db:
        generator = CandidateGenerator(neo4j_db)
        for product_name in cart_product_names:
            try:
                candidates = generator.generate_candidates(product_name)
                for cname, cinfo in candidates.items():
                    if cname in cart_product_set:
                        continue

                    # Prioritize accessories and compatibility
                    is_acc = "ACCESSORY" in cinfo.direct_relationships
                    is_compat = "COMPATIBLE_WITH" in cinfo.direct_relationships
                    base_score = 40.0
                    if is_acc:
                        base_score += 35.0
                    if is_compat:
                        base_score += 25.0

                    if cname not in all_candidates:
                        reasons = [f"Complements your {product_name}"]
                        if is_acc:
                            reasons.append("Essential accessory")
                        if is_compat:
                            reasons.append("Verified hardware compatibility")
                        all_candidates[cname] = {
                            "product": cname,
                            "score": min(base_score, 98.0),
                            "reasons": reasons,
                            "context": f"Pairs well with {product_name}",
                        }
                    else:
                        all_candidates[cname]["score"] = min(all_candidates[cname]["score"] + 15, 99.0)
                        all_candidates[cname]["reasons"].append(f"Also works with {product_name}")
            except Exception:
                continue

        behavior = get_user_behavior(current_user.id, db)
        purchased = set(behavior.get("purchased", []))

        cand_names = [r["product"] for r in all_candidates.values() if r["product"] not in purchased]
        info_map = enrich_products_info(cand_names, neo4j_db)

        results = []
        for r in all_candidates.values():
            if r["product"] in purchased or r["product"] not in info_map:
                continue
            r["product_info"] = info_map[r["product"]]
            results.append(r)

        results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "cart_products": cart_product_names,
        "recommendations": results[:8],
    }


@router.get("/category/{category_name}")
def category_recommendations(category_name: str, top_k: int = 6):
    """Return top picks in a category and popular accessories for that category."""
    with get_db() as neo4j_db:
        # Category products
        cat_rows = neo4j_db.run_query("MATCH (p:Product)", {"category": category_name})
        cat_rows.sort(key=lambda x: x.get("rating", 0), reverse=True)

        # Recommended accessories for products in this category
        acc_rows = neo4j_db.run_query(
            """
            MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: $category})
            MATCH (p)-[:ACCESSORY|COMPATIBLE_WITH]->(acc:Product)
            WHERE acc.category <> $category
            RETURN DISTINCT acc.name AS name
            LIMIT 10
            """,
            {"category": category_name},
        )
        acc_names = [r["name"] for r in acc_rows]
        info_map = enrich_products_info(acc_names, neo4j_db)
        accessories = list(info_map.values())

    return {
        "category": category_name,
        "top_picks": cat_rows[:top_k],
        "popular_accessories": accessories[:top_k],
    }


@router.get("")
def personalized_recommendations(
    top_k: int = Query(default=8, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Personalized recommendations for the home page.
    Automatically detects user category affinity, recent views, and cart additions,
    returning:
      - Recommended For You
      - Recently Viewed
      - Related To Your Interests (dynamic category top picks, e.g. 'Top Picks for Laptop Lovers')
      - Trending Products
    """
    with get_db() as neo4j_db:
        # Anonymous / Cold Start Experience
        if not current_user:
            all_prods = neo4j_db.run_query("MATCH (p:Product)")
            # Sort by rating and popularity
            all_prods.sort(key=lambda x: (x.get("rating", 0), x.get("review_count", 0)), reverse=True)
            trending = all_prods[:top_k]
            popular_laptops = [p for p in all_prods if p.get("category") == "Laptops"][:top_k]
            popular_audio = [p for p in all_prods if p.get("category") in ("Headphones", "Earbuds", "Speakers")][:top_k]

            return {
                "personalized": False,
                "message": "Welcome! Login to experience personalized graph recommendations.",
                "recommendations": [
                    {
                        "product": p["name"],
                        "score": 85.0,
                        "reasons": [f"Top rated in {p.get('category', 'Electronics')}", "Customer favorite"],
                        "product_info": p,
                    }
                    for p in trending
                ],
                "recently_viewed": [],
                "related_to_interests": None,
                "trending": trending,
                "popular_laptops": popular_laptops,
                "popular_accessories": popular_audio,
            }

        # Logged-in user experience
        behavior = get_user_behavior(current_user.id, db)
        purchased_set = set(behavior.get("purchased", []))
        viewed_list = behavior.get("viewed", [])
        viewed_set = set(viewed_list)

        # Detect top interest category
        cat_counts = Counter(behavior.get("viewed_categories", []))
        top_interest_category = cat_counts.most_common(1)[0][0] if cat_counts else None

        # Context products (most recent views/cart)
        context_products = []
        if behavior["viewed"]:
            context_products.extend(behavior["viewed"][:4])
        if behavior["carted"]:
            context_products.extend([p for p in behavior["carted"] if p not in context_products][:2])

        # If user has no history yet, fallback gracefully
        if not context_products:
            all_prods = neo4j_db.run_query("MATCH (p:Product)")
            all_prods.sort(key=lambda x: x.get("rating", 0), reverse=True)
            return {
                "personalized": False,
                "message": "Browse products to unlock personalized graph recommendations!",
                "recommendations": [
                    {
                        "product": p["name"],
                        "score": 82.0,
                        "reasons": ["Featured product"],
                        "product_info": p,
                    }
                    for p in all_prods[:top_k]
                ],
                "recently_viewed": [],
                "related_to_interests": None,
                "trending": all_prods[:top_k],
            }

        # Candidate generation across context products
        generator = CandidateGenerator(neo4j_db)
        all_candidates: dict[str, dict] = {}

        for cp_name in context_products[:3]:
            try:
                candidates = generator.generate_candidates(cp_name)
                for cand_name, cinfo in candidates.items():
                    if cand_name in purchased_set or cand_name in viewed_set:
                        continue
                    if cand_name not in all_candidates:
                        all_candidates[cand_name] = {
                            "name": cand_name,
                            "info": cinfo,
                            "context": cp_name,
                            "frequency": 1,
                        }
                    else:
                        all_candidates[cand_name]["frequency"] += 1
            except Exception:
                continue

        cand_names = list(all_candidates.keys())
        info_map = enrich_products_info(cand_names, neo4j_db)

        scored_recs = []
        behavior["top_categories"] = [c for c, _ in cat_counts.most_common(3)]
        for name, item in all_candidates.items():
            if name not in info_map:
                continue
            cand_data = info_map[name]
            score, reasons = calculate_transparent_score(
                candidate_name=name,
                candidate_info=item["info"],
                candidate_data=cand_data,
                context_product_data={"name": item["context"]},
                user_behavior=behavior,
            )
            # Multi-context boost
            if item["frequency"] > 1:
                score = min(score + (item["frequency"] - 1) * 6.0, 99.0)
                reasons.append(f"Recommended across {item['frequency']} items you browsed")

            scored_recs.append({
                "product": name,
                "score": score,
                "reasons": reasons,
                "product_info": cand_data,
            })

        scored_recs.sort(key=lambda r: r["score"], reverse=True)

        # Recently viewed enriched
        recent_info_map = enrich_products_info(viewed_list[:6], neo4j_db)
        recently_viewed = [recent_info_map[n] for n in viewed_list[:6] if n in recent_info_map]

        # Related to User's Top Interests
        related_to_interests = None
        if top_interest_category:
            cat_prods = neo4j_db.run_query("MATCH (p:Product)", {"category": top_interest_category})
            interest_items = [p for p in cat_prods if p["name"] not in viewed_set and p["name"] not in purchased_set]
            interest_items.sort(key=lambda x: x.get("rating", 0), reverse=True)
            if interest_items:
                related_to_interests = {
                    "category": top_interest_category,
                    "title": f"Top Picks for {top_interest_category} Enthusiasts",
                    "products": interest_items[:top_k],
                }

    return {
        "personalized": True,
        "behavior_signals": {
            "viewed_count": len(behavior["viewed"]),
            "searched_count": len(behavior["searched"]),
            "carted_count": len(behavior["carted"]),
            "wishlisted_count": len(behavior["wishlisted"]),
            "top_category": top_interest_category,
        },
        "recommendations": scored_recs[:top_k],
        "recently_viewed": recently_viewed,
        "related_to_interests": related_to_interests,
    }
