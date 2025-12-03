import asyncio
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from playwright.async_api import async_playwright, APIRequestContext, APIResponse


# ---- Data model -------------------------------------------------------------

@dataclass
class MercadonaProduct:
    id: int
    name: str
    price: float          # base price (per unit / pack)
    price_raw: str        # raw string, e.g. "1,25 €"
    category_name: str    # top-level group, e.g. "Huevos, leche y mantequilla"
    subcategory_name: str # subcategory, e.g. "Leche y bebidas vegetales"
    category_id: int
    subcategory_id: int
    unit_size: Optional[str] = None   # e.g. "1 l"
    unit_price: Optional[str] = None  # e.g. "0,45 €/l"
    slug: Optional[str] = None        # used to build product URL if needed


# ---- Helpers ----------------------------------------------------------------

def _extract_number_from_price(text: str) -> Optional[float]:
    """
    Extract a float from price strings like '1,25 €', '0.79€', etc.
    Returns None if no number is found.
    """
    if not text:
        return None
    m = re.search(r"(\d+[.,]\d+|\d+)", text)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _matches_query(name: str, query: str) -> bool:
    """
    Slightly smarter matching:
    - lowercases everything
    - splits the query into words of length >= 3
    - requires ALL those words to be present in the product name
    So "leche entera" will match "Leche UHT entera 1L Hacendado".
    """
    name_l = name.lower()
    # words of 3+ chars to avoid matching "de", "y", etc.
    words = [w for w in re.split(r"\s+", query.lower().strip()) if len(w) >= 3]
    if not words:
        return False
    return all(w in name_l for w in words)


async def _ensure_ok(resp: APIResponse, context: str) -> None:
    """
    Manual version of raise_for_status() for Playwright APIResponse.
    """
    if not resp.ok:
        try:
            body = await resp.text()
        except Exception:
            body = "<failed to read body>"
        raise RuntimeError(f"{context} failed with status {resp.status}: {body[:300]}")


# ---- HTTP calls -------------------------------------------------------------

async def fetch_categories(api: APIRequestContext) -> list:
    """
    Fetch /api/categories/ and return the 'results' list.
    """
    resp = await api.get("/api/categories/")
    await _ensure_ok(resp, "GET /api/categories/")
    data = await resp.json()
    return data["results"]  # list of top-level category groups


async def fetch_category_detail(api: APIRequestContext, category_id: int) -> dict:
    """
    Fetch a single category's full JSON from /api/categories/{id}/
    """
    resp = await api.get(f"/api/categories/{category_id}/")
    await _ensure_ok(resp, f"GET /api/categories/{category_id}/")
    return await resp.json()


# ---- Parsing -------------------------------------------------------------

def _collect_products_from_detail(category_detail: dict) -> List[dict]:
    """
    Mercadona sometimes puts products directly in 'products',
    and sometimes under nested 'categories' -> 'products'.

    This function returns a flat list of all product dicts in that detail.
    """
    products: List[dict] = []

    # Case 1: direct products list
    direct = category_detail.get("products")
    if isinstance(direct, list) and direct:
        products.extend(direct)

    # Case 2: nested subcategories with their own 'products'
    nested_cats = category_detail.get("categories") or []
    for sub in nested_cats:
        sub_products = sub.get("products") or []
        for p in sub_products:
            # store nested subcategory name for later if needed
            p["_nested_subcategory_name"] = sub.get("name")
        products.extend(sub_products)

    return products


def _parse_category_products(
    category_group: dict,
    category_detail: dict,
    fallback_subcat_name: str,
    fallback_subcat_id: int,
) -> List[MercadonaProduct]:
    """
    Parse products from a category_detail payload.
    """
    products_raw = _collect_products_from_detail(category_detail)

    group_name = category_group["name"]
    group_id = category_group["id"]

    # If the detail has its own name/id we use them; otherwise we keep the
    # fallback from the original 'subcat' object.
    base_subcat_name = category_detail.get("name") or fallback_subcat_name
    base_subcat_id = category_detail.get("id") or fallback_subcat_id

    parsed: List[MercadonaProduct] = []

    for p in products_raw:
        name = p.get("display_name") or p.get("name") or "Sin nombre"

        price_info = p.get("price_instructions", {}) or {}

        numeric_price = (
            price_info.get("unit_price")
            or price_info.get("bulk_price")
            or price_info.get("price")
        )

        price_str = (
            price_info.get("bulk_price_string")
            or price_info.get("unit_price_string")
            or price_info.get("price_string")
            or ""
        )

        if numeric_price is None:
            numeric_price = _extract_number_from_price(price_str)

        if numeric_price is None:
            # No price we can trust → skip
            continue

        # If we had a nested subcategory name, prefer that so you see
        # "Leche y bebidas vegetales" instead of some generic.
        nested_name = p.get("_nested_subcategory_name")
        final_subcat_name = nested_name or base_subcat_name

        product = MercadonaProduct(
            id=p.get("id"),
            name=name,
            price=float(numeric_price),
            price_raw=price_str,
            category_name=group_name,
            subcategory_name=final_subcat_name,
            category_id=group_id,
            subcategory_id=base_subcat_id,
            unit_size=price_info.get("unit_size"),
            unit_price=price_info.get("reference_price_string")
            or price_info.get("unit_price_string"),
            slug=p.get("slug"),
        )
        parsed.append(product)

    return parsed


# ---- High-level search -----------------------------------------------------

async def search_mercadona_cheapest(
    query: str,
    max_category_groups: Optional[int] = None,
) -> Tuple[Optional[MercadonaProduct], List[MercadonaProduct]]:
    """
    High-level function:

    - Spins up Playwright
    - Walks Mercadona categories
    - Filters products by query
    - Returns: (cheapest_product or None, sorted_matches_list)
    """
    async with async_playwright() as p:
        api = await p.request.new_context(base_url="https://tienda.mercadona.es")

        categories = await fetch_categories(api)

        if max_category_groups is not None:
            categories = categories[:max_category_groups]

        all_matches: List[MercadonaProduct] = []
        total_products_scanned = 0

        for group in categories:
            subcats = group.get("categories", []) or []

            for subcat in subcats:
                subcat_id = subcat["id"]
                subcat_name = subcat.get("name", "")

                detail = await fetch_category_detail(api, subcat_id)
                products = _parse_category_products(group, detail, subcat_name, subcat_id)

                total_products_scanned += len(products)

                for product in products:
                    if _matches_query(product.name, query):
                        all_matches.append(product)

        # Debug info
        print(f"[DEBUG] Scanned ~{total_products_scanned} products across {len(categories)} top-level groups.")

        if not all_matches:
            return None, []

        all_matches.sort(key=lambda p: p.price)
        cheapest = all_matches[0]
        return cheapest, all_matches


# ---- Script entrypoint -----------------------------------------------------

async def main():
    # 🔹 change this line to test different searches:
    query = "huevos"

    cheapest, matches = await search_mercadona_cheapest(query)

    if not matches:
        print(f"No products found for query: {query!r}")
        return

    print(f"Found {len(matches)} matching products for {query!r}:\n")

    # Show first 10 cheapest matches
    for p in matches[:10]:
        print(
            f"- {p.name} | {p.price} € ({p.price_raw or 'raw N/A'}) "
            f"| {p.category_name} / {p.subcategory_name}"
        )

    print("\nCheapest option:")
    c = cheapest
    print(
        f"{c.name} | {c.price} € ({c.price_raw or 'raw N/A'}) "
        f"| {c.category_name} / {c.subcategory_name}"
    )


if __name__ == "__main__":
    asyncio.run(main())
