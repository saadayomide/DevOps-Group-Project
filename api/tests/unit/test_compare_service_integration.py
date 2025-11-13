"""
Unit tests for compare_service.compare_basket() method
Tests the full integration with database
"""
import pytest
from app.services.compare_service import CompareService
from app.schemas import CompareRequest


class TestCompareBasket:
    """Test cases for compare_basket service method"""
    
    def test_picks_global_min_when_all_stores_have_prices(self, test_db, seed_test_data):
        """
        Test Case: Picks global min when all stores have prices
        
        Scenario: All 3 products exist at all 3 stores
        Expected: Each item should pick the store with minimum price
        - Milk: Target ($2.49) - cheapest
        - Bread: Kroger ($1.89) - cheapest
        - Eggs: Target ($3.29) - cheapest
        """
        service = CompareService()
        data = seed_test_data
        
        request = CompareRequest(
            items=["Milk", "Bread", "Eggs"],
            stores=["Walmart", "Target", "Kroger"]
        )
        
        response = service.compare_basket(request, test_db)
        
        # All items should be matched
        assert len(response.unmatched) == 0
        assert len(response.items) == 3
        
        # Verify each item picked the cheapest store
        item_stores = {item.name: item.store for item in response.items}
        assert item_stores["Milk"] == "Target"  # $2.49 is cheapest
        assert item_stores["Bread"] == "Kroger"  # $1.89 is cheapest
        assert item_stores["Eggs"] == "Target"  # $3.29 is cheapest
        
        # Verify prices
        item_prices = {item.name: item.price for item in response.items}
        assert item_prices["Milk"] == 2.49
        assert item_prices["Bread"] == 1.89
        assert item_prices["Eggs"] == 3.29
        
        # Verify store totals
        store_totals = {total.store: total.total for total in response.storeTotals}
        # Target: Milk ($2.49) + Eggs ($3.29) = $5.78
        # Kroger: Bread ($1.89) = $1.89
        # Walmart: $0 (no items selected)
        assert store_totals["Target"] == pytest.approx(5.78, abs=0.01)
        assert store_totals["Kroger"] == pytest.approx(1.89, abs=0.01)
        assert store_totals["Walmart"] == pytest.approx(0.0, abs=0.01)
        
        # Overall total should be minimum total if all items bought at one store
        # Target: $2.49 + $2.19 + $3.29 = $7.97
        # Kroger: $2.79 + $1.89 + $3.69 = $8.37
        # Walmart: $2.99 + $1.99 + $3.49 = $8.47
        # Minimum is Target: $7.97
        assert response.overallTotal == pytest.approx(7.97, abs=0.01)
    
    def test_returns_unmatched_if_product_doesnt_exist(self, test_db, seed_test_data):
        """
        Test Case: Returns unmatched if a product doesn't exist
        
        Scenario: Request includes a product that doesn't exist in database
        Expected: Product should be in unmatched list
        """
        service = CompareService()
        seed_test_data  # Seed data
        
        request = CompareRequest(
            items=["Milk", "NonexistentProduct", "Bread"],
            stores=["Walmart", "Target", "Kroger"]
        )
        
        response = service.compare_basket(request, test_db)
        
        # Should have 2 matched items and 1 unmatched
        assert len(response.items) == 2
        assert len(response.unmatched) == 1
        assert "NonexistentProduct" in response.unmatched
        
        # Matched items should be Milk and Bread
        matched_names = [item.name for item in response.items]
        assert "Milk" in matched_names
        assert "Bread" in matched_names
        assert "NonexistentProduct" not in matched_names
    
    def test_tie_resolved_by_running_store_totals(self, test_db, seed_test_data):
        """
        Test Case: Tie resolved by running store totals
        
        Scenario: Two stores have the same price for an item
        Expected: Store with lower current basket subtotal should be chosen
        This minimizes store switches
        """
        service = CompareService()
        data = seed_test_data
        
        # Add a product with same price at multiple stores
        # Create a new product
        from app.models import Product, Price
        new_product = Product(name="Butter", category="Dairy")
        test_db.add(new_product)
        test_db.commit()
        test_db.refresh(new_product)
        
        # Add prices: same price at Walmart and Target, different at Kroger
        # Walmart: $4.00, Target: $4.00 (tie), Kroger: $5.00
        walmart = data["supermarkets"][0]
        target = data["supermarkets"][1]
        kroger = data["supermarkets"][2]
        
        test_db.add(Price(product_id=new_product.id, store_id=walmart.id, price=4.00))
        test_db.add(Price(product_id=new_product.id, store_id=target.id, price=4.00))
        test_db.add(Price(product_id=new_product.id, store_id=kroger.id, price=5.00))
        test_db.commit()
        
        # First request: Milk (Target $2.49), then Butter (tie between Walmart and Target)
        # At this point, Target has $2.49, Walmart has $0
        # So Walmart should be chosen (lower basket subtotal)
        request = CompareRequest(
            items=["Milk", "Butter"],
            stores=["Walmart", "Target", "Kroger"]
        )
        
        response = service.compare_basket(request, test_db)
        
        # Verify Milk went to Target (cheapest)
        milk_item = next(item for item in response.items if item.name == "Milk")
        assert milk_item.store == "Target"
        assert milk_item.price == 2.49
        
        # Verify Butter went to Walmart (tie-breaker: lower basket subtotal)
        butter_item = next(item for item in response.items if item.name == "Butter")
        assert butter_item.store == "Walmart"  # Should choose Walmart due to tie-breaker
        assert butter_item.price == 4.00
        
        # Verify store totals
        store_totals = {total.store: total.total for total in response.storeTotals}
        assert store_totals["Target"] == pytest.approx(2.49, abs=0.01)
        assert store_totals["Walmart"] == pytest.approx(4.00, abs=0.01)
    
    def test_empty_items_returns_error(self, test_db, seed_test_data):
        """
        Test Case: Empty items should be handled (validation happens in route)
        
        Note: This test verifies the service handles empty items gracefully
        The route should return 400/422 before calling the service
        """
        service = CompareService()
        seed_test_data
        
        request = CompareRequest(
            items=[],
            stores=["Walmart", "Target"]
        )
        
        # Service should handle empty items gracefully
        response = service.compare_basket(request, test_db)
        
        # Should return empty response
        assert len(response.items) == 0
        assert len(response.unmatched) == 0
        assert response.overallTotal == 0.0
    
    def test_unknown_stores_ignored_silently(self, test_db, seed_test_data):
        """
        Test Case: Unknown stores are ignored silently
        
        Scenario: Request includes stores that don't exist
        Expected: Unknown stores are ignored, comparison happens with known stores only
        """
        service = CompareService()
        seed_test_data
        
        request = CompareRequest(
            items=["Milk", "Bread"],
            stores=["Walmart", "UnknownStore", "Target"]
        )
        
        response = service.compare_basket(request, test_db)
        
        # Should still work with known stores (Walmart, Target)
        assert len(response.items) == 2
        
        # Store totals should only include known stores
        store_names = [total.store for total in response.storeTotals]
        assert "Walmart" in store_names
        assert "Target" in store_names
        assert "UnknownStore" not in store_names
    
    def test_partial_product_match(self, test_db, seed_test_data):
        """
        Test Case: Some products exist, some don't
        
        Scenario: Mix of existing and non-existing products
        Expected: Existing products matched, non-existing in unmatched
        """
        service = CompareService()
        seed_test_data
        
        request = CompareRequest(
            items=["Milk", "Bread", "Nonexistent1", "Eggs", "Nonexistent2"],
            stores=["Walmart", "Target", "Kroger"]
        )
        
        response = service.compare_basket(request, test_db)
        
        # Should match 3 products (Milk, Bread, Eggs)
        assert len(response.items) == 3
        assert len(response.unmatched) == 2
        
        matched_names = [item.name for item in response.items]
        assert "Milk" in matched_names
        assert "Bread" in matched_names
        assert "Eggs" in matched_names
        
        assert "Nonexistent1" in response.unmatched
        assert "Nonexistent2" in response.unmatched
    
    def test_case_insensitive_matching(self, test_db, seed_test_data):
        """
        Test Case: Product and store names are matched case-insensitively
        """
        service = CompareService()
        seed_test_data
        
        request = CompareRequest(
            items=["milk", "BREAD", "eggs"],  # Mixed case
            stores=["walmart", "TARGET", "kroger"]  # Mixed case
        )
        
        response = service.compare_basket(request, test_db)
        
        # Should match all products
        assert len(response.items) == 3
        assert len(response.unmatched) == 0

