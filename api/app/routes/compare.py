"""
Product comparison routes
Core algorithm: For each requested item, choose the cheapest price across selected stores.
"""
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Tuple, List, Optional
from decimal import Decimal
import logging
from app.db import get_db
from app.models import Price, Product, Supermarket
from app.schemas import CompareRequest, CompareResponse, CompareItem, StoreTotal
from app.services.normalization import normalize_item_name

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CompareResponse)
async def compare_items(
    request: CompareRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Compare items across stores - Core algorithm implementation
    
    Goal: For each requested item, choose the cheapest price across the selected stores.
    
    Algorithm (MVP, deterministic):
    1. Normalize items and stores. Reject if empty → 400 BadRequest.
    2. Resolve product IDs by exact name match on LOWER(products.name).
    3. Query all prices for product_id IN (...) and store_id IN (...) in one query.
    4. For each requested item: pick min price with tie-breaker (lower basket subtotal).
    5. Build response arrays: items[], storeTotals[], overallTotal, unmatched[].
    
    Request body:
    {
        "items": ["milk", "bread", "eggs"],
        "stores": ["Walmart", "Target", "Kroger"]
    }
    """
    # Step 1: Normalize items and stores. Reject if empty → 400 BadRequest
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="items cannot be empty"
        )
    
    if not request.stores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="stores cannot be empty"
        )
    
    # Normalize item names
    normalized_items = [normalize_item_name(item) for item in request.items]
    
    # Normalize store names (simple lowercase and trim)
    normalized_store_names = [store.lower().strip() for store in request.stores]
    
    # Step 2: Resolve product IDs by exact name match on LOWER(products.name)
    # Since we use normalization (synonyms, whitespace collapsing), we need to normalize
    # both the item names and product names for matching
    # Fetch all products once (MVP scale - one query is fine)
    all_products = db.query(Product).all()
    
    # Build a mapping of normalized product name to product
    # Normalize product names (lowercase, trim, collapse whitespace, apply synonyms)
    normalized_product_name_to_product: Dict[str, Product] = {}
    for product in all_products:
        # Normalize product name using the same normalization as items
        normalized_product_name = normalize_item_name(product.name)
        # If multiple products have the same normalized name, keep the first one
        if normalized_product_name and normalized_product_name not in normalized_product_name_to_product:
            normalized_product_name_to_product[normalized_product_name] = product
    
    # Map requested items to products using exact normalized name match
    item_to_product: Dict[str, Optional[Product]] = {}
    unmatched: List[str] = []
    
    for i, item in enumerate(request.items):
        normalized_item = normalized_items[i]
        
        # Match normalized item name to normalized product name
        if normalized_item in normalized_product_name_to_product:
            item_to_product[item] = normalized_product_name_to_product[normalized_item]
        else:
            item_to_product[item] = None
            unmatched.append(item)
    
    # Step 3: Resolve store IDs
    all_stores = db.query(Supermarket).all()
    store_name_to_store: Dict[str, Supermarket] = {}
    for store in all_stores:
        normalized_store_name = store.name.lower().strip()
        if normalized_store_name not in store_name_to_store:
            store_name_to_store[normalized_store_name] = store
    
    # Get store objects for requested stores
    store_objs: List[Supermarket] = []
    for store_name in request.stores:
        normalized_store_name = store_name.lower().strip()
        if normalized_store_name in store_name_to_store:
            store_objs.append(store_name_to_store[normalized_store_name])
    
    if not store_objs:
        # No stores found - return all items as unmatched
        return CompareResponse(
            items=[],
            storeTotals=[],
            overallTotal=0.0,
            unmatched=request.items
        )
    
    # Get product IDs and store IDs for the query
    product_ids = [p.id for item, p in item_to_product.items() if p is not None]
    store_ids = [s.id for s in store_objs]
    
    # Step 3: Query all prices for product_id IN (...) and store_id IN (...) in one query
    # Map to prices_map[(product_id, store_id)] = price
    # Performance: One round-trip SQL query for all prices (MVP scale)
    prices_map: Dict[Tuple[int, int], Decimal] = {}
    
    if product_ids and store_ids:
        # Single query to get all prices - avoids N+1 queries
        prices = db.query(Price).filter(
            Price.product_id.in_(product_ids),
            Price.store_id.in_(store_ids)
        ).all()
        
        # Build prices_map: (product_id, store_id) -> price (as Decimal)
        # If multiple prices exist for same product-store, take the minimum price
        for price in prices:
            key = (price.product_id, price.store_id)
            price_value = price.price  # Already Decimal from database
            if key not in prices_map:
                prices_map[key] = price_value
            else:
                # Take minimum price if multiple prices exist
                prices_map[key] = min(prices_map[key], price_value)
    
    # Step 4: For each requested item: pick min price with tie-breaker
    # Maintain running store_totals for tie-breaking
    compare_items: List[CompareItem] = []
    store_totals: Dict[int, Decimal] = {store_id: Decimal('0.00') for store_id in store_ids}
    store_id_to_name: Dict[int, str] = {s.id: s.name for s in store_objs}
    
    # Process items in order
    for item in request.items:
        product = item_to_product.get(item)
        if product is None:
            # Already added to unmatched, skip
            continue
        
        # Find all candidate stores with a price for this product
        candidates: List[Tuple[int, Decimal]] = []
        for store_id in store_ids:
            key = (product.id, store_id)
            if key in prices_map:
                price = prices_map[key]
                candidates.append((store_id, price))
        
        if not candidates:
            # No price found for this product at any store
            if item not in unmatched:
                unmatched.append(item)
            continue
        
        # Pick the store with minimum price
        # Tie-breaker: if two stores have the same price, pick the one with lower current basket subtotal
        # This helps balance baskets across stores (as specified in algorithm)
        min_price = min(candidates, key=lambda x: x[1])[1]
        
        # Find all stores with the minimum price (ties)
        min_price_stores = [(store_id, price) for store_id, price in candidates if price == min_price]
        
        # If there's a tie (multiple stores with same price), use tie-breaker
        if len(min_price_stores) > 1:
            # Sort by current basket subtotal (ascending), then by store_id for deterministic selection
            # Pick store with lower current basket subtotal (as per algorithm specification)
            min_price_stores.sort(key=lambda x: (store_totals[x[0]], x[0]))
        
        # Select the store (first one after sorting - has minimum price and lowest current basket)
        selected_store_id, selected_price = min_price_stores[0]
        selected_store_name = store_id_to_name[selected_store_id]
        
        # Add to compare_items (cast Decimal to float for response)
        compare_items.append(CompareItem(
            name=item,
            store=selected_store_name,
            price=float(selected_price)
        ))
        
        # Update running store_totals (used for tie-breaking in next iterations)
        store_totals[selected_store_id] += selected_price
    
    # Step 5: Build response arrays
    # Build storeTotals list (cast Decimal to float)
    # store_totals contains the totals for selected items at each store
    store_totals_list = [
        StoreTotal(store=store_id_to_name[store_id], total=float(total))
        for store_id, total in store_totals.items()
    ]
    
    # Calculate overallTotal (minimum total if you bought all items at one store)
    # This represents the best deal if you shopped at a single store
    # Calculate total for each store if all matched items were bought there
    store_complete_totals: Dict[int, Decimal] = {}
    for store_id in store_ids:
        store_total = Decimal('0.00')
        for item in request.items:
            product = item_to_product.get(item)
            if product is None:
                continue
            key = (product.id, store_id)
            if key in prices_map:
                store_total += prices_map[key]
        store_complete_totals[store_id] = store_total
    
    # overallTotal is the minimum total across all stores
    if store_complete_totals.values():
        stores_with_all_items = [total for total in store_complete_totals.values() if total > 0]
        if stores_with_all_items:
            overall_total = float(min(stores_with_all_items))
        else:
            overall_total = 0.0
    else:
        overall_total = 0.0
    
    # Log compare operation with counts (Team C will see this in App Insights)
    items_requested = len(request.items)
    items_matched = len(compare_items)
    items_unmatched = len(unmatched)
    
    logger.info(
        "Compare operation completed",
        extra={
            "endpoint": "/compare",
            "method": "POST",
            "items_requested": items_requested,
            "items_matched": items_matched,
            "items_unmatched": items_unmatched,
            "stores_count": len(store_objs)
        }
    )
    
    return CompareResponse(
        items=compare_items,
        storeTotals=store_totals_list,
        overallTotal=overall_total,
        unmatched=unmatched
    )
