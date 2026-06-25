from django.db.models import Q


def normalize(query: str) -> str:
    return query.strip().lower()


def score_tier1(product, query: str) -> float:
    """Category match. Sub-rank by how many tags also match the query."""
    tags = [t.lower() for t in (product.tags or [])]
    matching_tags = sum(1 for t in tags if query in t)
    # Base 0.70, up to 0.30 bonus from tags (capped)
    bonus = min(matching_tags * 0.06, 0.30)
    return round(0.70 + bonus, 4)


def score_tier2(product, query: str) -> float:
    """Tag match. Exact tag hit scores higher than partial."""
    tags = [t.lower() for t in (product.tags or [])]
    exact = any(t == query for t in tags)
    partial = any(query in t for t in tags)
    if exact:
        return 0.65
    if partial:
        # More partial matches = slightly higher
        count = sum(1 for t in tags if query in t)
        return round(0.40 + min(count * 0.04, 0.20), 4)
    return 0.40


def score_tier3(product, query: str) -> float:
    """Name / description match. Name match > description match."""
    name_match = query in product.product_name.lower()
    desc_match = query in product.product_description.lower()
    if name_match and desc_match:
        return 0.35
    if name_match:
        return 0.30
    if desc_match:
        return 0.15
    return 0.10


def rank_reason(tier: int, product, query: str) -> str:
    if tier == 1:
        return f"Category match ({product.category})"
    if tier == 2:
        tags = [t for t in (product.tags or []) if query in t.lower()]
        return f"Tag match ({', '.join(tags)})"
    return "Name/description match"


def search_products(queryset, query: str):
    """
    Returns a list of dicts sorted by relevance score descending.
    Each dict contains product data + relevance_score + rank_reason.
    """
    q = normalize(query)
    if not q:
        return []

    # Pull only matching products from DB using OR filter
    matching = queryset.filter(
        Q(category__icontains=q) |
        Q(tags__icontains=q) |
        Q(product_name__icontains=q) |
        Q(product_description__icontains=q)
    )

    results = []
    for product in matching:
        category_lower = product.category.lower()
        tags_lower = [t.lower() for t in (product.tags or [])]

        # Determine tier
        if q in category_lower:
            tier = 1
            score = score_tier1(product, q)
        elif any(q in t for t in tags_lower):
            tier = 2
            score = score_tier2(product, q)
        else:
            tier = 3
            score = score_tier3(product, q)

        results.append({
            'id': product.id,
            'product_name': product.product_name,
            'product_description': product.product_description,
            'category': product.category,
            'tags': product.tags,
            'relevance_score': score,
            'rank_reason': rank_reason(tier, product, q),
            '_tier': tier,
        })

    # Sort: tier first (1 > 2 > 3), then score descending
    results.sort(key=lambda x: (x['_tier'], -x['relevance_score']))

    # Remove internal _tier key before returning
    for r in results:
        r.pop('_tier')

    return results
