"""
Product comparison service
"""
from typing import List, Optional, Dict, Tuple
from app.schemas import ProductComparison, ComparisonResult, CompareItem, StoreTotal, CompareResponse
from app.services.normalization import normalize_product_name, calculate_similarity


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
        # Only consider stores that have at least one item (total > 0)
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

