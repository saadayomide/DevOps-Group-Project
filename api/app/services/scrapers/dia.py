import asyncio
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Page


# ------------------ Data model ------------------ #

@dataclass
class SearchResult:
    name: str
    price: float
    price_raw: str
    url: Optional[str] = None
    extra: dict = None


# ------------------ Helpers ------------------ #

def parse_price(text: str) -> Optional[float]:
    """
    Extract a float from a string that contains a price like:
    '1,25 €', '0.79€', '2 €', etc.
    """
    if not text:
        return None
    m = re.search(r"(\d+[.,]\d+|\d+)\s*€", text)
    if not m:
        # fallback: any number
        m = re.search(r"(\d+[.,]\d+|\d+)", text)
        if not m:
            return None
    num = m.group(1).replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return None


def extract_name_from_text(full_text: str) -> Optional[str]:
    """
    Heuristic to guess a product name from all the text inside a card:
    - Split into lines
    - Remove empty / very short lines
    - Prefer lines without '€' or 'añadir'
    - Return the longest such line
    """
    if not full_text:
        return None

    lines = [ln.strip() for ln in full_text.splitlines()]
    lines = [ln for ln in lines if len(ln) >= 3]

    def is_probably_name(ln: str) -> bool:
        low = ln.lower()
        if "€" in low:
            return False
        if "añadir" in low:
            return False
        if "€/kilo" in low or "€/litro" in low:
            return False
        if "oferta" in low:
            return False
        return True

    candidates = [ln for ln in lines if is_probably_name(ln)]
    if not candidates:
        candidates = lines

    if not candidates:
        return None

    return max(candidates, key=len)


async def accept_cookies_if_any(page: Page) -> None:
    """
    Try a few common ways to accept cookie popups.
    We ignore failures.
    """
    # 1) Try by role + name
    for label in ["Aceptar", "Aceptar todo", "Aceptar todas", "Acepto"]:
        try:
            btn = page.get_by_role("button", name=label)
            await btn.click(timeout=2000)
            return
        except Exception:
            pass

    # 2) Try generic button containing 'Acept'
    try:
        buttons = await page.query_selector_all("button")
        for b in buttons:
            txt = (await b.inner_text()).strip().lower()
            if "acept" in txt:
                try:
                    await b.click(timeout=2000)
                    return
                except Exception:
                    pass
    except Exception:
        pass


# ------------------ DIA scraper ------------------ #

async def search_cheapest_dia(query: str) -> Tuple[Optional[SearchResult], List[SearchResult]]:
    """
    Search DIA online for a query using:
        https://www.dia.es/search?q=<query>
    Scrape product cards generically and return
        (cheapest_relevant_result, all_relevant_results_sorted_by_price).

    Relevance = product name contains all “important” words from the query
    (words of length >= 3), e.g. 'leche' and 'entera'.
    """
    # preprocess query tokens once
    tokens = [w for w in re.split(r"\s+", query.lower().strip()) if len(w) >= 3]

    async with async_playwright() as p:
        # headless=False so you can see what's going on; set to True later
        browser = await p.chromium.launch(headless=False)
        page: Page = await browser.new_page()

        # 1) Build search URL (this is the one you sent)
        search_url = f"https://www.dia.es/search?q={quote_plus(query)}"
        print(f"[DEBUG] Opening {search_url}")
        await page.goto(search_url, wait_until="domcontentloaded")

        # 2) Cookies
        await accept_cookies_if_any(page)

        # 3) Wait a bit for results
        await page.wait_for_timeout(4000)

        # 4) Grab candidate product containers
        #    Start with <article> (common pattern for product cards)
        cards = []
        try:
            cards = await page.query_selector_all("article")
        except Exception:
            pass

        # Add some extra candidates by class name heuristic
        extra_cards = []
        try:
            extra_cards = await page.query_selector_all(
                "div[class*='product'], li[class*='product']"
            )
        except Exception:
            pass

        # Combine & dedupe
        card_set = {id(c): c for c in cards + extra_cards}
        cards = list(card_set.values())

        print(f"[DEBUG] Found {len(cards)} potential product elements")

        results: List[SearchResult] = []

        for idx, card in enumerate(cards):
            try:
                full_text = await card.inner_text()
            except Exception:
                continue

            full_text = full_text.strip()
            if not full_text:
                continue

            # Try to extract a price
            price = parse_price(full_text)
            if price is None:
                continue

            # Try to extract a name
            name = extract_name_from_text(full_text)
            if not name:
                continue

            name_low = name.lower()

            # ----------------- RELEVANCE FILTERS ----------------- #
            # 1) Require that name contains all query tokens
            if tokens and not all(t in name_low for t in tokens):
                # not relevant to the search (e.g. candy when searching 'leche entera')
                continue

            # 2) Require a product link → skip nested elements like 'Añadir'
            href = None
            try:
                # look for <a> inside the card
                link_el = await card.query_selector("a")
                if link_el:
                    href = await link_el.get_attribute("href")
                    if href and href.startswith("#"):
                        href = None
            except Exception:
                href = None

            if href:
                if href.startswith("/"):
                    href = "https://www.dia.es" + href
            else:
                # no real product link → treat as non-product (e.g. just an "Añadir" button)
                continue
            # ----------------------------------------------------- #

            results.append(
                SearchResult(
                    name=name,
                    price=price,
                    price_raw=f"{price} €",
                    url=href,
                    extra={"card_index": idx},
                )
            )

        await browser.close()

        if not results:
            return None, []

        results.sort(key=lambda r: r.price)
        return results[0], results


# ------------------ Test entrypoint ------------------ #

async def main():
    query = "huevos"  # change to test different searches

    cheapest, all_results = await search_cheapest_dia(query)

    if not all_results:
        print(f"No relevant products found for query: {query!r}")
        return

    print(f"\nFound {len(all_results)} relevant products for {query!r}.\n")
    print("Top 10 cheapest:\n")
    for r in all_results[:10]:
        print(f"- {r.price:.2f} € | {r.name} | {r.url or 'no url'}")

    print("\nCheapest option:")
    print(f"=> {cheapest.price:.2f} € | {cheapest.name}")
    if cheapest.url:
        print(f"   {cheapest.url}")


if __name__ == "__main__":
    asyncio.run(main())
