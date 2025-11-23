from fastapi import APIRouter, HTTPException
from typing import List, Dict

from models import CompareRequest, CompareResponse
from service import compare_items, SAMPLE_PRICES

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/supermarkets")
async def get_supermarkets():
    """
    Return a simple list of supermarkets with numeric ids.
    """
    return [{"id": i + 1, "name": name} for i, name in enumerate(SAMPLE_PRICES.keys())]


@router.get("/products")
async def get_products():
    """
    Aggregate all distinct product names across SAMPLE_PRICES, return with numeric ids.
    """
    products = set()
    for store_prices in SAMPLE_PRICES.values():
        products.update(store_prices.keys())
    products = sorted(products)
    return [{"id": i + 1, "name": p} for i, p in enumerate(products)]


@router.get("/prices")
async def get_prices():
    """
    Return prices linking supermarket_id and product_id to match TestDataConsistency expectations.
    """
    # Build maps consistent with get_supermarkets/get_products
    supermarkets = list(SAMPLE_PRICES.keys())
    products = sorted({p for s in SAMPLE_PRICES.values() for p in s.keys()})
    product_index = {p: i + 1 for i, p in enumerate(products)}
    supermarket_index = {s: i + 1 for i, s in enumerate(supermarkets)}

    prices_list = []
    for s_name, prod_map in SAMPLE_PRICES.items():
        sid = supermarket_index[s_name]
        for prod_name, price in prod_map.items():
            prices_list.append(
                {"supermarket_id": sid, "product_id": product_index[prod_name], "price": float(price)}
            )
    return prices_list


@router.post("/compare", response_model=CompareResponse)
async def api_compare(payload: CompareRequest):
    """
    Wrapper for compare_items that validates stores and returns the CompareResponse.
    """
    # Validate store names if provided
    if payload.stores:
        invalid = [s for s in payload.stores if s not in SAMPLE_PRICES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid store(s): {', '.join(invalid)}")

    resp = compare_items(payload, prices=SAMPLE_PRICES)
    return resp
# ...existing code...