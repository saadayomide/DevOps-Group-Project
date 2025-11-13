"""
Unit tests for compare service helper methods
Tests utility methods that don't require database
"""
import pytest
from app.services.compare_service import CompareService
from app.schemas import ProductComparison


def test_find_cheapest():
    """Test finding cheapest product"""
    service = CompareService()
    comparisons = [
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=1,
            store_name="Store A",
            price=2.99
        ),
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=2,
            store_name="Store B",
            price=2.49
        ),
    ]
    
    cheapest = service.find_cheapest(comparisons)
    assert cheapest.price == 2.49


def test_find_most_expensive():
    """Test finding most expensive product"""
    service = CompareService()
    comparisons = [
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=1,
            store_name="Store A",
            price=2.99
        ),
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=2,
            store_name="Store B",
            price=2.49
        ),
    ]
    
    most_expensive = service.find_most_expensive(comparisons)
    assert most_expensive.price == 2.99


def test_calculate_average_price():
    """Test calculating average price"""
    service = CompareService()
    comparisons = [
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=1,
            store_name="Store A",
            price=2.0
        ),
        ProductComparison(
            product_id=1,
            product_name="Milk",
            store_id=2,
            store_name="Store B",
            price=4.0
        ),
    ]
    
    average = service.calculate_average_price(comparisons)
    assert average == 3.0

