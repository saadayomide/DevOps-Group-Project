from typing import Dict, List, Optional, Tuple
from .models import CompareRequest, CompareResponse, Recommendation

# Example in-memory price table for TeamC development. Replace with real DB/queries.
SAMPLE_PRICES = {
    "Mercadona": {"milk": 1.0, "bread": 0.8, "eggs": 1.5},
    "Carrefour": {"milk": 1.1, "bread": 0.75, "eggs": 1.6},
    "Lidl": {"milk": 0.95, "bread": 0.85, "eggs": 1.4},
}


def _normalize(name: str) -> str:
    return name.strip().lower()


def compare_items(req: CompareRequest, prices: Optional[Dict[str, Dict[str, float]]] = None) -> CompareResponse:
    prices = prices or SAMPLE_PRICES
    stores = req.stores if req.stores else list(prices.keys())
    stores = [s for s in stores if s in prices]

    recommendations: List[Recommendation] = []
    store_totals: Dict[str, float] = {s: 0.0 for s in stores}

    for raw_item in req.items:
        item = _normalize(raw_item)
        found_prices: Dict[str, float] = {}
        for s in stores:
            p = prices.get(s, {}).get(item)
            if p is not None:
                found_prices[s] = float(p)

        if not found_prices:
            # item not found in any store -> skip
            continue

        cheapest_store, cheapest_price = min(found_prices.items(), key=lambda kv: kv[1])
        for s, p in found_prices.items():
            store_totals[s] += p
        recommendations.append(
            Recommendation(product=item, cheapest_store=cheapest_store, price=cheapest_price, all_prices=found_prices)
        )

    total_cost = sum(r.price for r in recommendations)

    # savings: difference between choosing cheapest-per-item vs choosing first store totals (if stores provided)
    savings = 0.0
    if stores:
        first_store = stores[0]
        first_tot = 0.0
        for r in recommendations:
            first_price = r.all_prices.get(first_store)
            if first_price is not None:
                first_tot += first_price
            else:
                # if first store missing price, approximate by cheapest (no savings change)
                first_tot += r.price
        savings = max(0.0, first_tot - total_cost)

    return CompareResponse(
        recommendations=recommendations,
        total_cost=round(total_cost, 2),
        savings=round(savings, 2),
        store_totals={k: round(v, 2) for k, v in store_totals.items()},
    )