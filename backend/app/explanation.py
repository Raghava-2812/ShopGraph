"""
ShopGraph - Explanation Generator
app/explanation.py

Turns structured scoring signals into human-readable recommendation reasons.
"""

from app.candidate_generator import CandidateInfo


# Friendly display names for relationship types
_REL_LABELS: dict[str, str] = {
    "COMPATIBLE_WITH": "Directly compatible with the purchased product",
    "ACCESSORY":       "Accessory for the purchased product",
    "WORKS_WITH":      "Works with the purchased product",
    "SIMILAR_TO":      "Similar product to the one purchased",
}


def generate_reasons(
    purchased_product: str,
    candidate: CandidateInfo,
) -> list[str]:
    """
    Build a list of human-readable reason strings for a recommendation.

    Args:
        purchased_product: Name of the product the user purchased.
        candidate:         CandidateInfo with relationship signals.

    Returns:
        A list of reason strings (at least one guaranteed).
    """
    reasons: list[str] = []

    # 1. Direct relationship reasons
    for rel in candidate.direct_relationships:
        label = _REL_LABELS.get(rel, f"Related via {rel}")
        reasons.append(label)

    # 2. Shared feature reasons
    for feature in candidate.shared_features:
        reasons.append(f"Shares {feature} feature with {purchased_product}")

    # 3. Shared use-case reasons
    for use_case in candidate.shared_use_cases:
        reasons.append(f"Useful for {use_case}")

    # 4. Same category — only add if not already explained
    if candidate.same_category and not reasons:
        reasons.append("In the same product category")

    # Fallback
    if not reasons:
        reasons.append("Relevant product in the knowledge graph")

    return reasons
