"""
ShopGraph - Recommendations Router
app/routers/recommendations.py

Routes:
  GET /recommendations                      - Personalized for logged-in user
  GET /recommendations/product/{name}       - Product-context recommendations
  GET /recommendations/cart                 - Cart-based recommendations

Integrates the existing Neo4j recommendation engine with user behavior data from SQLite.

Scoring model (transparent, no ML):
  Graph Score (from existing engine):
    0.40 × Relationship Score
    0.25 × Feature Score
    0.15 × Category Score
    0.10 × Use Case Score
    0.10 × Similarity Score
  
  Personalization Boost:
    +5  if user recently VIEWED this product's category
    +8  if user recently SEARCHED for related terms
    +10 if user has WISHLISTED related product
    +3  if user recently VIEWED a similar product
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.sqlite_db import get_sqlite_db, UserEvent, CartItem, Cart, User
from app.auth import get_optional_user
from app.database import get_db
from app.recommender import ProductRecommender
from app.candidate_generator import CandidateGenerator, CandidateInfo
from app.explanation import generate_reasons

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


# ── Behavior helpers ──────────────────────────────────────────────────────────

def get_user_behavior(user_id: int, db: Session, days: int = 30) -> dict:
    """
    Fetch user behavior signals from the last `days` days.
    Returns categorized behavior data.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    events = db.query(UserEvent).filter(
        UserEvent.user_id == user_id,
        UserEvent.created_at >= since,
    ).order_by(UserEvent.created_at.desc()).all()
    
    behavior = {
        "viewed": [],
        "searched": [],
        "carted": [],
        "purchased": [],
        "wishlisted": [],
    }
    
    for e in events:
        if e.event_type == "VIEW" and e.product_name:
            behavior["viewed"].append(e.product_name)
        elif e.event_type == "SEARCH" and e.search_query:
            behavior["searched"].append(e.search_query)
        elif e.event_type == "ADD_TO_CART" and e.product_name:
            behavior["carted"].append(e.product_name)
        elif e.event_type == "PURCHASE" and e.product_name:
            behavior["purchased"].append(e.product_name)
        elif e.event_type == "WISHLIST" and e.product_name:
            behavior["wishlisted"].append(e.product_name)
    
    return behavior


def apply_personalization_boost(
    recommendations: list[dict],
    behavior: dict,
    neo4j_db,
) -> list[dict]:
    """
    Apply behavior-based score boost to recommendations.
    
    Boost formula (additive, transparent):
      +3  if candidate was recently viewed
      +5  if candidate is in same category as a recently viewed product
      +8  if candidate matches a recent search term
      +10 if candidate was wishlisted
    """
    if not behavior:
        return recommendations
    
    viewed_set = set(behavior.get("viewed", []))
    wishlisted_set = set(behavior.get("wishlisted", []))
    searches = behavior.get("searched", [])
    purchased_set = set(behavior.get("purchased", []))
    
    # Get categories of recently viewed products
    viewed_categories = set()
    if viewed_set:
        view_list = list(viewed_set)[:10]
        query = """
        MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
        WHERE p.name IN $names
        RETURN DISTINCT c.name AS category
        """
        rows = neo4j_db.run_query(query, {"names": view_list})
        viewed_categories = {r["category"] for r in rows}
    
    for rec in recommendations:
        boost = 0.0
        boost_reasons = []
        
        candidate_name = rec["product"]
        
        # +3 if recently viewed
        if candidate_name in viewed_set:
            boost += 3.0
            boost_reasons.append(f"You recently viewed {candidate_name}")
        
        # +10 if wishlisted
        if candidate_name in wishlisted_set:
            boost += 10.0
            boost_reasons.append(f"You have {candidate_name} in your wishlist")
        
        # Get candidate category for category match
        cat_query = """
        MATCH (p:Product {name: $name})-[:BELONGS_TO]->(c:Category)
        RETURN c.name AS category
        """
        cat_rows = neo4j_db.run_query(cat_query, {"name": candidate_name})
        if cat_rows:
            candidate_category = cat_rows[0]["category"]
            # +5 if in same category as recently viewed
            if candidate_category in viewed_categories:
                boost += 5.0
                boost_reasons.append(f"Similar to products you recently viewed")
        
        # +8 if name matches a search term
        for search_term in searches:
            if search_term.lower() in candidate_name.lower():
                boost += 8.0
                boost_reasons.append(f"Matches your recent search for '{search_term}'")
                break
        
        rec["score"] = min(round(rec["score"] + boost, 2), 100.0)
        if boost_reasons:
            rec["reasons"] = boost_reasons + rec["reasons"]
    
    # Re-sort after boost
    recommendations.sort(key=lambda r: r["score"], reverse=True)
    return recommendations


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/product/{product_name}")
def recommend_for_product(
    product_name: str,
    top_k: int = Query(default=5, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Get recommendations for a specific product.
    Automatically called when user opens a product page.
    Optionally personalized if user is logged in.
    """
    with get_db() as neo4j_db:
        recommender = ProductRecommender(neo4j_db)
        try:
            results = recommender.recommend(product_name, top_k=top_k * 2)  # get extra for filtering
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
    
    if not results:
        return {
            "context_product": product_name,
            "recommendations": [],
            "sections": {"you_may_also_like": [], "compatible_with": [], "accessories": []},
        }
    
    # Convert to dicts
    recs = [
        {"product": r.product, "score": r.score, "reasons": r.reasons}
        for r in results
    ]
    
    # Apply personalization if user is logged in
    if current_user:
        behavior = get_user_behavior(current_user.id, db)
        # Exclude already purchased products
        purchased = set(behavior.get("purchased", []))
        recs = [r for r in recs if r["product"] not in purchased]
        recs = apply_personalization_boost(recs, behavior, None)  # skipping cat boost here for speed
    
    # Categorize into sections using Neo4j relationship data
    with get_db() as neo4j_db:
        compat_query = """
        MATCH (p:Product {name: $name})-[:COMPATIBLE_WITH|WORKS_WITH]->(c:Product)
        RETURN c.name AS name
        """
        acc_query = """
        MATCH (p:Product {name: $name})-[:ACCESSORY]->(c:Product)
        RETURN c.name AS name  
        """
        sim_query = """
        MATCH (p:Product {name: $name})-[:SIMILAR_TO]->(c:Product)
        RETURN c.name AS name
        """
        
        compat_names = {r["name"] for r in neo4j_db.run_query(compat_query, {"name": product_name})}
        acc_names = {r["name"] for r in neo4j_db.run_query(acc_query, {"name": product_name})}
        sim_names = {r["name"] for r in neo4j_db.run_query(sim_query, {"name": product_name})}
    
    compatible = [r for r in recs if r["product"] in compat_names]
    accessories = [r for r in recs if r["product"] in acc_names]
    similar = [r for r in recs if r["product"] in sim_names]
    
    # "You May Also Like" = similar + anything not in the other two
    categorized = set(r["product"] for r in compatible) | set(r["product"] for r in accessories)
    you_may_like = [r for r in recs if r["product"] not in categorized]
    
    return {
        "context_product": product_name,
        "top_k": top_k,
        "recommendations": recs[:top_k],
        "sections": {
            "you_may_also_like": you_may_like[:4],
            "compatible_with": compatible[:4],
            "accessories": accessories[:4],
        },
    }


@router.get("/cart")
def recommend_for_cart(
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Get recommendations based on cart contents.
    Returns 'Complete Your Setup' suggestions.
    """
    if not current_user:
        return {"recommendations": [], "message": "Login to get cart recommendations"}
    
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return {"recommendations": []}
    
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        return {"recommendations": []}
    
    cart_product_names = [item.product_name for item in cart_items]
    cart_product_set = set(cart_product_names)
    
    # Generate candidates for all cart products
    all_candidates: dict[str, dict] = {}
    
    with get_db() as neo4j_db:
        generator = CandidateGenerator(neo4j_db)
        for product_name in cart_product_names:
            try:
                candidates = generator.generate_candidates(product_name)
                for cname, cinfo in candidates.items():
                    if cname not in cart_product_set:
                        if cname not in all_candidates:
                            reasons = generate_reasons(product_name, cinfo)
                            all_candidates[cname] = {
                                "product": cname,
                                "score": len(cinfo.direct_relationships) * 20 + len(cinfo.shared_features) * 5,
                                "reasons": reasons,
                                "context": f"Pairs well with {product_name}",
                            }
                        else:
                            # Boost if recommended by multiple cart products
                            all_candidates[cname]["score"] = min(all_candidates[cname]["score"] + 10, 100)
            except Exception:
                continue
    
    # Apply behavior-based filtering
    behavior = get_user_behavior(current_user.id, db)
    purchased = set(behavior.get("purchased", []))
    
    recs = [r for r in all_candidates.values() if r["product"] not in purchased]
    recs.sort(key=lambda r: r["score"], reverse=True)
    
    return {
        "cart_products": cart_product_names,
        "recommendations": recs[:6],
    }


@router.get("")
def personalized_recommendations(
    top_k: int = Query(default=8, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_sqlite_db),
):
    """
    Personalized recommendations for the home page.
    Uses the user's recent behavior to find relevant products.
    Falls back to popular/featured products for new users.
    """
    if not current_user:
        # Return popular/featured products for anonymous users
        with get_db() as neo4j_db:
            query = """
            MATCH (p:Product)
            OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
            OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
            RETURN p.name AS name, p.price AS price, p.description AS description,
                   cat.name AS category, b.name AS brand
            LIMIT $limit
            """
            rows = neo4j_db.run_query(query, {"limit": top_k})
        return {
            "personalized": False,
            "recommendations": [
                {"product": r["name"], "score": 70.0, "reasons": ["Popular product"], "product_info": r}
                for r in rows
            ]
        }
    
    behavior = get_user_behavior(current_user.id, db)
    
    # Determine context products from behavior (most recent first)
    context_products = []
    if behavior["viewed"]:
        context_products.extend(behavior["viewed"][:3])
    if behavior["purchased"]:
        context_products.extend(behavior["purchased"][:2])
    if behavior["carted"]:
        context_products.extend(behavior["carted"][:2])
    
    purchased_set = set(behavior["purchased"])
    viewed_set = set(behavior["viewed"])
    context_set = set(context_products)
    
    if not context_products:
        # New user with no history — return featured products
        with get_db() as neo4j_db:
            query = """
            MATCH (p:Product)
            OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
            OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
            RETURN p.name AS name, p.price AS price, p.description AS description,
                   cat.name AS category, b.name AS brand
            LIMIT $limit
            """
            rows = neo4j_db.run_query(query, {"limit": top_k})
        return {
            "personalized": False,
            "message": "Browse products to get personalized recommendations!",
            "recommendations": [
                {"product": r["name"], "score": 70.0, "reasons": ["Featured product"], "product_info": r}
                for r in rows
            ]
        }
    
    # Generate recommendations from all context products
    all_candidates: dict[str, dict] = {}
    
    with get_db() as neo4j_db:
        for context_product in context_products[:3]:  # limit to avoid slowness
            try:
                recommender = ProductRecommender(neo4j_db)
                results = recommender.recommend(context_product, top_k=10)
                for r in results:
                    if r.product not in purchased_set and r.product not in context_set:
                        if r.product not in all_candidates:
                            all_candidates[r.product] = {
                                "product": r.product,
                                "score": r.score,
                                "reasons": r.reasons,
                            }
                        else:
                            # Boost if recommended by multiple context products
                            all_candidates[r.product]["score"] = min(
                                all_candidates[r.product]["score"] + 5, 100.0
                            )
            except Exception:
                continue
    
    recs = list(all_candidates.values())
    
    # Apply personalization boost
    with get_db() as neo4j_db:
        recs = apply_personalization_boost(recs, behavior, neo4j_db)
    
    recs.sort(key=lambda r: r["score"], reverse=True)
    
    # Enrich with product info
    with get_db() as neo4j_db:
        product_names = [r["product"] for r in recs[:top_k]]
        if product_names:
            info_query = """
            MATCH (p:Product)
            WHERE p.name IN $names
            OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
            OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
            RETURN p.name AS name, p.price AS price, p.description AS description,
                   cat.name AS category, b.name AS brand
            """
            info_rows = neo4j_db.run_query(info_query, {"names": product_names})
            info_map = {r["name"]: r for r in info_rows}
            for rec in recs:
                rec["product_info"] = info_map.get(rec["product"], {})
    
    return {
        "personalized": True,
        "behavior_signals": {
            "viewed_count": len(behavior["viewed"]),
            "searched_count": len(behavior["searched"]),
            "purchased_count": len(behavior["purchased"]),
        },
        "recommendations": recs[:top_k],
    }
