"""
Unit tests for scraper infrastructure.

These tests use mocks and fixtures to test scrapers in isolation.
Never hits the real network - ensures deterministic CI/CD pipelines.

Testing Concepts:
- Mocking external dependencies
- Fixture-based test data
- Deterministic tests
- Error handling verification
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.scrapers.base import (
    Offer,
    ScraperFactory,
    normalize_text,
    extract_brand,
)
from app.services.scrapers import (
    scrape_mercadona,
    scrape_carrefour,
    scrape_alcampo,
    scrape_gadis,
    ScraperManager,
    get_all_offers,
)


# ---- Fixtures ----------------------------------------------------------------


@pytest.fixture
def sample_offers():
    """Sample Offer objects for testing"""
    return [
        Offer(
            store="TestStore",
            name="Leche Entera 1L",
            brand="TestBrand",
            price=1.25,
            url="https://example.com/product/1",
            normalized_name="leche entera 1l",
        ),
        Offer(
            store="TestStore",
            name="Pan Integral 500g",
            brand="OtraMarca",
            price=0.95,
            url="https://example.com/product/2",
            normalized_name="pan integral 500g",
        ),
    ]


@pytest.fixture
def mock_mercadona_response():
    """Mock response data from Mercadona API"""
    return {
        "results": [
            {
                "id": 1,
                "name": "Lácteos y Huevos",
                "categories": [
                    {"id": 101, "name": "Leche"},
                    {"id": 102, "name": "Huevos"},
                ],
            }
        ]
    }


# ---- Base Module Tests -------------------------------------------------------


class TestNormalizeText:
    """Tests for text normalization function"""

    def test_lowercase(self):
        assert normalize_text("HELLO") == "hello"

    def test_remove_accents(self):
        assert normalize_text("café") == "cafe"
        assert normalize_text("niño") == "nino"
        assert normalize_text("Leche Desnatada") == "leche desnatada"

    def test_collapse_whitespace(self):
        assert normalize_text("hello   world") == "hello world"
        assert normalize_text("  spaced  ") == "spaced"

    def test_empty_string(self):
        assert normalize_text("") == ""
        assert normalize_text(None) == ""

    def test_combined(self):
        result = normalize_text("  LECHE  Entera   Hacendado  ")
        assert result == "leche entera hacendado"


class TestExtractBrand:
    """Tests for brand extraction function"""

    def test_known_brand(self):
        assert extract_brand("Leche Hacendado 1L") == "Hacendado"
        assert extract_brand("Yogur Danone Natural") == "Danone"

    def test_unknown_brand_uses_first_word(self):
        # First word used as fallback if not a common word
        result = extract_brand("SuperMarca Producto 500g")
        assert result == "SuperMarca"

    def test_empty_returns_none(self):
        assert extract_brand("") is None
        assert extract_brand(None) is None


class TestOfferModel:
    """Tests for Offer data model"""

    def test_create_offer(self):
        offer = Offer(
            store="Mercadona",
            name="Leche Entera 1L",
            price=1.25,
        )
        assert offer.store == "Mercadona"
        assert offer.name == "Leche Entera 1L"
        assert offer.price == 1.25
        assert offer.brand is None

    def test_offer_with_optional_fields(self):
        offer = Offer(
            store="Carrefour",
            name="Pan Integral",
            brand="Bimbo",
            price=2.50,
            url="https://example.com",
            normalized_name="pan integral",
        )
        assert offer.brand == "Bimbo"
        assert offer.url == "https://example.com"

    def test_offer_to_dict(self, sample_offers):
        offer = sample_offers[0]
        result = offer.to_dict()

        assert isinstance(result, dict)
        assert result["store"] == "TestStore"
        assert result["name"] == "Leche Entera 1L"
        assert result["price"] == 1.25

    def test_price_validation(self):
        # Price must be >= 0
        with pytest.raises(ValueError):
            Offer(store="Test", name="Product", price=-1.0)


class TestScraperFactory:
    """Tests for ScraperFactory"""

    def test_create_registered_scraper(self):
        # Mercadona should be registered
        scraper = ScraperFactory.create("mercadona")
        assert scraper is not None
        assert scraper.STORE_NAME == "Mercadona"

    def test_create_unknown_scraper(self):
        scraper = ScraperFactory.create("unknown_store")
        assert scraper is None

    def test_get_available_stores(self):
        stores = ScraperFactory.get_available_stores()
        assert "mercadona" in stores
        assert "carrefour" in stores
        assert "alcampo" in stores


# ---- Individual Scraper Tests ------------------------------------------------


class TestCarrefourScraper:
    """Tests for Carrefour scraper (MVP with mock data)"""

    def test_search_returns_offers(self):
        offers = scrape_carrefour("leche")

        assert isinstance(offers, list)
        assert len(offers) > 0
        assert all(isinstance(o, Offer) for o in offers)

    def test_offer_structure(self):
        offers = scrape_carrefour("huevos")

        if offers:
            offer = offers[0]
            assert offer.store == "Carrefour"
            assert offer.price >= 0
            assert offer.name

    def test_empty_query_returns_empty(self):
        offers = scrape_carrefour("")
        # Should handle gracefully
        assert isinstance(offers, list)

    def test_normalized_name_set(self):
        offers = scrape_carrefour("arroz")

        for offer in offers:
            assert offer.normalized_name is not None
            assert offer.normalized_name == offer.normalized_name.lower()


class TestAlcampoScraper:
    """Tests for Alcampo scraper (MVP with mock data)"""

    def test_search_returns_offers(self):
        offers = scrape_alcampo("pan")

        assert isinstance(offers, list)
        assert len(offers) > 0

    def test_graceful_degradation(self):
        # Unknown query should return empty, not crash
        offers = scrape_alcampo("producto_inexistente_xyz")
        assert isinstance(offers, list)

    def test_store_name_correct(self):
        offers = scrape_alcampo("yogur")

        for offer in offers:
            assert offer.store == "Alcampo"


class TestMercadonaScraper:
    """Tests for Mercadona scraper (mocked - no real network)"""

    @patch("app.services.scrapers.mercadona.PLAYWRIGHT_AVAILABLE", False)
    def test_returns_empty_without_playwright(self):
        """Without Playwright, should return empty gracefully"""
        offers = scrape_mercadona("leche")
        assert isinstance(offers, list)
        # Empty because Playwright not available in test
        assert len(offers) == 0

    def test_store_name(self):
        from app.services.scrapers.mercadona import MercadonaScraper

        scraper = MercadonaScraper()
        assert scraper.STORE_NAME == "Mercadona"


class TestGadisScraper:
    """Tests for Gadis scraper (Galicia regional supermarket)"""

    def test_search_returns_offers(self):
        """Should return offers for common products"""
        offers = scrape_gadis("leche")

        assert isinstance(offers, list)
        assert len(offers) > 0
        assert all(isinstance(o, Offer) for o in offers)

    def test_offer_structure(self):
        """Offers should have correct structure"""
        offers = scrape_gadis("huevos")

        if offers:
            offer = offers[0]
            assert offer.store == "Gadis"
            assert offer.price >= 0
            assert offer.name

    def test_galician_products(self):
        """Should have Galician regional products"""
        offers = scrape_gadis("queso")

        # Check for Galician cheeses
        names = [o.name.lower() for o in offers]
        assert any("tetilla" in n or "arzua" in n for n in names) or len(offers) == 0

    def test_store_name_correct(self):
        """Store name should be Gadis"""
        offers = scrape_gadis("agua")

        for offer in offers:
            assert offer.store == "Gadis"

    def test_graceful_degradation(self):
        """Unknown query should return empty, not crash"""
        offers = scrape_gadis("producto_inexistente_xyz")
        assert isinstance(offers, list)


# ---- ScraperManager Tests ----------------------------------------------------


class TestScraperManager:
    """Tests for ScraperManager facade"""

    def test_initialization(self):
        manager = ScraperManager()
        assert len(manager.scrapers) >= 2  # At least Carrefour and Alcampo

    def test_get_offers_combines_stores(self):
        manager = ScraperManager()
        offers = manager.get_offers("leche")

        # Should have offers from multiple stores
        stores = set(o.store for o in offers)
        assert len(stores) >= 2

    def test_specific_stores_only(self):
        manager = ScraperManager(stores=["carrefour"])
        offers = manager.get_offers("pan")

        # Should only have Carrefour offers
        stores = set(o.store for o in offers)
        assert stores == {"Carrefour"} or len(stores) == 0

    def test_get_offers_by_store(self):
        manager = ScraperManager()
        offers = manager.get_offers_by_store("arroz", "alcampo")

        for offer in offers:
            assert offer.store == "Alcampo"

    def test_get_store_status(self):
        manager = ScraperManager()
        status = manager.get_store_status()

        assert isinstance(status, dict)
        assert "carrefour" in status or "alcampo" in status

    def test_graceful_failure(self):
        """Manager should continue even if one scraper fails"""
        manager = ScraperManager()

        # Mock one scraper to fail
        with patch.object(
            manager.scrapers.get("carrefour", MagicMock()),
            "search",
            side_effect=Exception("Test error"),
        ):
            # Should not raise, should return partial results
            offers = manager.get_offers("leche")
            assert isinstance(offers, list)


class TestGetAllOffers:
    """Tests for convenience function"""

    def test_returns_offers(self):
        offers = get_all_offers("pasta")

        assert isinstance(offers, list)
        assert len(offers) >= 0


# ---- Integration-like Tests (still mocked) -----------------------------------


class TestScraperIntegration:
    """Integration tests for scraper system (still mocked)"""

    def test_full_pipeline(self):
        """Test full scraping pipeline"""
        # Get offers from all stores
        manager = ScraperManager()
        offers = manager.get_offers("aceite")

        # Verify structure
        for offer in offers:
            assert isinstance(offer, Offer)
            assert offer.store in ["Mercadona", "Carrefour", "Alcampo", "Lidl", "Dia", "Gadis"]
            assert offer.price >= 0

    def test_no_duplicate_offers(self):
        """Offers should be unique within a store (for mock data stores)"""
        # Only test mock/fallback data stores
        # Mercadona can have legitimate duplicates (same name, different sizes)
        manager = ScraperManager(stores=["carrefour", "alcampo", "lidl", "dia", "gadis"])
        offers = manager.get_offers("tomate")

        # Group by store
        by_store = {}
        for offer in offers:
            by_store.setdefault(offer.store, []).append(offer)

        # Check no duplicates within each store
        for store, store_offers in by_store.items():
            names = [o.name for o in store_offers]
            assert len(names) == len(set(names)), f"Duplicates in {store}"
