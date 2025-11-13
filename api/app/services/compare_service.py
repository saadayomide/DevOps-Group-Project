"""
Product comparison service
"""
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from app.schemas import ProductComparison, ComparisonResult, CompareItem, StoreTotal, CompareResponse, CompareRequest
from app.services.normalization import normalize_product_name, normalize_item_name, calculate_similarity
from app.models import Product, Supermarket, Price


class CompareService:
    """Service for comparing products and prices"""
    
    def __init__(self):
        self.min_similarity_threshold = 0.5
    
    def find_best_matches(
        self,
        query: str,
        products: List[dict],
        threshold: Optional[float] = None
    ) -> List[dict]:
        """
        Find best matching products based on name similarity
        """
        if threshold is None:
            threshold = self.min_similarity_threshold
        
        normalized_query = normalize_product_name(query)
        matches = []
        
        for product in products:
            product_name = product.get('name', '')
            similarity = calculate_similarity(normalized_query, product_name)
            
            if similarity >= threshold:
                matches.append({
                    **product,
                    'similarity': similarity
                })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return matches
    
    def find_cheapest(self, comparisons: List[ProductComparison]) -> Optional[ProductComparison]:
        """Find the cheapest product from comparisons"""
        if not comparisons:
            return None
        return min(comparisons, key=lambda x: x.price)
    
    def find_most_expensive(self, comparisons: List[ProductComparison]) -> Optional[ProductComparison]:
        """Find the most expensive product from comparisons"""
        if not comparisons:
            return None
        return max(comparisons, key=lambda x: x.price)
    
    def calculate_average_price(self, comparisons: List[ProductComparison]) -> float:
        """Calculate average price from comparisons"""
        if not comparisons:
            return 0.0
        return sum(c.price for c in comparisons) / len(comparisons)
    
    def calculate_price_difference(
        self,
        comparison1: ProductComparison,
        comparison2: ProductComparison
    ) -> float:
        """Calculate price difference between two comparisons"""
        return abs(comparison1.price - comparison2.price)
    
    def get_price_statistics(self, comparisons: List[ProductComparison]) -> dict:
        """Get price statistics from comparisons"""
        if not comparisons:
            return {
                'count': 0,
                'min': 0.0,
                'max': 0.0,
                'average': 0.0,
                'median': 0.0
            }
        
        prices = sorted([c.price for c in comparisons])
        count = len(prices)
        
        return {
            'count': count,
            'min': prices[0],
            'max': prices[-1],
            'average': sum(prices) / count,
            'median': prices[count // 2] if count % 2 == 1 else (prices[count // 2 - 1] + prices[count // 2]) / 2
        }
    
    def compare_basket(
        self,
        request: CompareRequest,
        db: Session
    ) -> CompareResponse:
        """
        Compare a basket of items across stores
        
        Core algorithm: For each requested item, choose the cheapest price across selected stores.
        
        Args:
            request: CompareRequest with items and stores
            db: SQLAlchemy database session
        
        Returns:
            CompareResponse with items, store totals, overall total, and unmatched items
        """
        # Step 1: Normalize items and stores
        normalized_items = [normalize_item_name(item) for item in request.items]
        normalized_store_names = [store.lower().strip() for store in request.stores]
        
        # Step 2: Resolve product IDs by exact name match on normalized names
        all_products = db.query(Product).all()
        
        # Build a mapping of normalized product name to product
        normalized_product_name_to_product: Dict[str, Product] = {}
        for product in all_products:
            normalized_product_name = normalize_item_name(product.name)
            if normalized_product_name and normalized_product_name not in normalized_product_name_to_product:
                normalized_product_name_to_product[normalized_product_name] = product
        
        # Map requested items to products using exact normalized name match
        item_to_product: Dict[str, Optional[Product]] = {}
        unmatched: List[str] = []
        
        for i, item in enumerate(request.items):
            normalized_item = normalized_items[i]
            
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
        
        # Step 4: Query all prices for product_id IN (...) and store_id IN (...) in one query
        prices_map: Dict[Tuple[int, int], Decimal] = {}
        
        if product_ids and store_ids:
            prices = db.query(Price).filter(
                Price.product_id.in_(product_ids),
                Price.store_id.in_(store_ids)
            ).all()
            
            # Build prices_map: (product_id, store_id) -> price (as Decimal)
            for price in prices:
                key = (price.product_id, price.store_id)
                price_value = price.price
                if key not in prices_map:
                    prices_map[key] = price_value
                else:
                    # Take minimum price if multiple prices exist
                    prices_map[key] = min(prices_map[key], price_value)
        
        # Step 5: For each requested item: pick min price with tie-breaker
        compare_items: List[CompareItem] = []
        store_totals: Dict[int, Decimal] = {store_id: Decimal('0.00') for store_id in store_ids}
        store_id_to_name: Dict[int, str] = {s.id: s.name for s in store_objs}
        
        # Process items in order
        for item in request.items:
            product = item_to_product.get(item)
            if product is None:
                continue
            
            # Find all candidate stores with a price for this product
            candidates: List[Tuple[int, Decimal]] = []
            for store_id in store_ids:
                key = (product.id, store_id)
                if key in prices_map:
                    price = prices_map[key]
                    candidates.append((store_id, price))
            
            if not candidates:
                if item not in unmatched:
                    unmatched.append(item)
                continue
            
            # Pick the store with minimum price
            min_price = min(candidates, key=lambda x: x[1])[1]
            
            # Find all stores with the minimum price (ties)
            min_price_stores = [(store_id, price) for store_id, price in candidates if price == min_price]
            
            # If there's a tie, use tie-breaker (lower current basket subtotal)
            if len(min_price_stores) > 1:
                min_price_stores.sort(key=lambda x: (store_totals[x[0]], x[0]))
            
            # Select the store
            selected_store_id, selected_price = min_price_stores[0]
            selected_store_name = store_id_to_name[selected_store_id]
            
            # Add to compare_items
            compare_items.append(CompareItem(
                name=item,
                store=selected_store_name,
                price=float(selected_price)
            ))
            
            # Update running store_totals (used for tie-breaking in next iterations)
            store_totals[selected_store_id] += selected_price
        
        # Step 6: Build response arrays
        store_totals_list = [
            StoreTotal(store=store_id_to_name[store_id], total=float(total))
            for store_id, total in store_totals.items()
        ]
        
        # Calculate overallTotal (minimum total if you bought all items at one store)
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
        
        return CompareResponse(
            items=compare_items,
            storeTotals=store_totals_list,
            overallTotal=overall_total,
            unmatched=unmatched
        )
    
    def compare_items_across_stores(
        self,
        items: List[str],
        stores: List[str],
        item_prices: Dict[Tuple[str, str], float]
    ) -> CompareResponse:
        """
        Compare items across stores and calculate totals
        
        Args:
            items: List of item names to compare
            stores: List of store names to compare across
            item_prices: Dictionary mapping (item_name, store_name) to price
        
        Returns:
            CompareResponse with items, store totals, overall total, and unmatched items
        """
        compare_items: List[CompareItem] = []
        unmatched: List[str] = []
        store_totals: Dict[str, float] = {store: 0.0 for store in stores}
        
        # Process each item
        for item in items:
            item_found = False
            
            # Check if item exists at any store
            for store in stores:
                key = (item, store)
                if key in item_prices:
                    price = item_prices[key]
                    compare_items.append(CompareItem(
                        name=item,
                        store=store,
                        price=price
                    ))
                    store_totals[store] += price
                    item_found = True
            
            # Track unmatched items
            if not item_found:
                unmatched.append(item)
        
        # Build store totals list
        store_totals_list = [
            StoreTotal(store=store, total=total)
            for store, total in store_totals.items()
        ]
        
        # Calculate overall total (minimum total across stores that have items - best deal)
        stores_with_items = [total for total in store_totals.values() if total > 0]
        if stores_with_items:
            overall_total = min(stores_with_items)
        else:
            overall_total = 0.0
        
        return CompareResponse(
            items=compare_items,
            storeTotals=store_totals_list,
            overallTotal=overall_total,
            unmatched=unmatched
        )
