"""
RentWiz – Production Selenium Scraper for MagicBricks
Extracts REAL rental listings with genuine external URLs.

Usage:
    cd backend
    python scraper/magicbricks_scraper.py --city Mumbai --bhk 2 --max 30 --save
    python scraper/magicbricks_scraper.py --city Bangalore --bhk 3 --max 25 --save --no-headless
"""
import argparse
import hashlib
import logging
import time
import random
import re
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, StaleElementReferenceException,
        WebDriverException,
    )
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False
    logger.error("Selenium not installed. Run: pip install selenium")


# ── Selector sets (tried in order; MagicBricks changes layouts) ──────────────
CARD_SELECTORS = [
    ".mb-srp__card",
    "[data-q='srp-property-card']",
    ".m-srp-card",
    ".srpcard",
    ".property-card",
    "article[class*='card']",
]

RENT_SELECTORS = [
    ".mb-srp__card__price--amount",
    "[data-q='prop-price']",
    ".m-srp-card__price--main",
    ".mb-srp__card--price",
    "[class*='price']",
]

TITLE_SELECTORS = [
    ".mb-srp__card--title",
    "[data-q='prop-name']",
    ".m-srp-card__title",
    "h2[class*='title']",
    "h3[class*='title']",
]

LOCATION_SELECTORS = [
    ".mb-srp__card__society--name",
    "[data-q='prop-location']",
    ".m-srp-card__location",
    "[class*='location']",
    "[class*='society']",
]

AREA_SELECTORS = [
    ".mb-srp__card__summary--value",
    "[data-q='prop-area']",
    "[class*='area']",
    "[class*='summary']",
]


# ── Chrome driver setup ──────────────────────────────────────────────────────

def _build_driver(headless: bool = True) -> "webdriver.Chrome":
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=en-US,en")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)
    # Mask webdriver fingerprint
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


# ── Parsing helpers ──────────────────────────────────────────────────────────

def _parse_rent(text: str, context: str = "") -> int | None:
    if not text:
        return None
    # Skip per-sqft prices
    combined = (text + " " + context).lower()
    if "sq ft" in combined or "/sqft" in combined or "per sq" in combined:
        return None
    clean = text.replace(",", "").replace("\u20b9", "").lower().strip()
    # Crore → sale price, not rent
    if re.search(r"\d.*cr(?:ore)?", clean):
        return None
    # Lakh format: "1.2 L" or "1.2 lakh"
    m = re.search(r"(\d+(?:\.\d+)?)\s*l(?:akh)?", clean)
    if m:
        val = int(float(m.group(1)) * 100_000)
        if 5_000 <= val <= 1_000_000:
            return val
    # Plain integer: must be realistic monthly rent
    m = re.search(r"(\d{4,7})", clean)
    if m:
        val = int(float(m.group(1)))
        if 5_000 <= val <= 1_000_000:
            return val
    return None


def _parse_area(text: str) -> int | None:
    if not text:
        return None
    text = text.replace(",", "")
    m = re.search(r"(\d{3,6})\s*(?:sq\.?\s*ft|sqft|sq)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{3,6})", text)
    if m:
        v = int(m.group(1))
        if 200 <= v <= 10000:
            return v
    return None


def _parse_bhk(text: str) -> int | None:
    m = re.search(r"(\d+)\s*(?:BHK|bhk|RK|rk|bedroom)", text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _safe_text(el, selectors: list[str]) -> str:
    for sel in selectors:
        try:
            found = el.find_element(By.CSS_SELECTOR, sel)
            t = found.text.strip()
            if t:
                return t
        except (NoSuchElementException, StaleElementReferenceException):
            continue
    return ""


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


# ── Core scraper ─────────────────────────────────────────────────────────────

def scrape_magicbricks(
    city: str = "Mumbai",
    bhk: int = 2,
    max_listings: int = 30,
    headless: bool = True,
) -> list[dict]:
    """
    Scrape real rental listings from MagicBricks.
    Returns only listings with REAL external URLs.
    Returns empty list if scraping fails (never returns fake data).
    """
    if not SELENIUM_OK:
        logger.error("Selenium is not installed — cannot scrape.")
        return []

    # MagicBricks uses specific city slug names in the URL
    CITY_SLUG_MAP = {
        "Delhi":     "New-Delhi",
        "Mumbai":    "Mumbai",
        "Bangalore": "Bangalore",
        "Hyderabad": "Hyderabad",
        "Pune":      "Pune",
        "Chennai":   "Chennai",
        "Kolkata":   "Kolkata",
        "Ahmedabad": "Ahmedabad",
    }
    city_slug = CITY_SLUG_MAP.get(city, city)
    bhk_param = f"{bhk}-BHK"
    url = (
        "https://www.magicbricks.com/property-for-rent/residential-real-estate"
        f"?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment"
        f"&cityName={city_slug}&BHK={bhk_param}"
    )

    driver = None
    listings = []

    try:
        logger.info(f"Opening MagicBricks: {bhk}BHK in {city}")
        logger.info(f"URL: {url}")
        driver = _build_driver(headless=headless)
        driver.get(url)

        # Wait for initial page load
        time.sleep(random.uniform(4, 6))

        # Scroll to trigger lazy loading
        logger.info("Scrolling to load listings...")
        last_count = 0
        for scroll in range(6):
            driver.execute_script("window.scrollBy(0, window.innerHeight * 1.5);")
            time.sleep(random.uniform(1.5, 2.5))
            # Check if cards appeared
            for sel in CARD_SELECTORS:
                c = driver.find_elements(By.CSS_SELECTOR, sel)
                if len(c) > last_count:
                    last_count = len(c)
                    logger.info(f"  Scroll {scroll+1}: found {last_count} cards ({sel})")
                    break

        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Find cards
        cards = []
        used_selector = None
        for sel in CARD_SELECTORS:
            found = driver.find_elements(By.CSS_SELECTOR, sel)
            if found:
                cards = found
                used_selector = sel
                logger.info(f"Using selector '{sel}': {len(cards)} cards")
                break

        if not cards:
            logger.warning("No listing cards found on page.")
            logger.info("Page source preview:")
            logger.info(driver.page_source[:500])
            return []

        logger.info(f"Extracting data from {min(len(cards), max_listings)} cards...")

        for i, card in enumerate(cards[:max_listings]):
            try:
                listing = _extract_card(card, city, bhk)
                if listing:
                    listings.append(listing)
                    logger.info(
                        f"  [{i+1}] {listing['location']} | "
                        f"₹{listing['actual_rent']:,} | "
                        f"{listing['area_sqft']} sqft | "
                        f"URL: {listing['listing_url'][:60] if listing.get('listing_url') else 'NONE'}"
                    )
                time.sleep(random.uniform(0.3, 0.8))
            except Exception as e:
                logger.debug(f"Card {i+1} error: {e}")
                continue

    except WebDriverException as e:
        logger.error(f"WebDriver error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected scraper error: {e}", exc_info=True)
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Only return listings with REAL urls (no mock/placeholder)
    real = [l for l in listings if _is_real_url(l.get("listing_url", ""))]
    logger.info(f"Scraped {len(listings)} total, {len(real)} with real URLs")
    return real


def _extract_card(card, city: str, default_bhk: int) -> dict | None:
    """Extract all fields from a listing card element."""
    try:
        # ── Title ────────────────────────────────────────────────────────────
        title = _safe_text(card, TITLE_SELECTORS) or f"{default_bhk}BHK Apartment"

        # ── Rent ─────────────────────────────────────────────────────────────
        rent_text = _safe_text(card, RENT_SELECTORS)
        actual_rent = _parse_rent(rent_text)
        if not actual_rent:
            # Try full card text as fallback
            full_text = card.text
            actual_rent = _parse_rent(full_text)
        if not actual_rent:
            return None  # Skip if no rent found

        # ── Area ─────────────────────────────────────────────────────────────
        area_text = _safe_text(card, AREA_SELECTORS)
        area_sqft = _parse_area(area_text) or _parse_area(card.text)
        if not area_sqft:
            area_sqft = 650  # reasonable default

        # ── BHK ──────────────────────────────────────────────────────────────
        bhk = _parse_bhk(title) or _parse_bhk(card.text) or default_bhk

        # ── Location ─────────────────────────────────────────────────────────
        location = _safe_text(card, LOCATION_SELECTORS) or city

        # ── URL ───────────────────────────────────────────────────────────────
        listing_url = None
        try:
            # Prefer anchor tags with /propertyDetails/ in href
            anchors = card.find_elements(By.TAG_NAME, "a")
            for a in anchors:
                href = a.get_attribute("href") or ""
                if "magicbricks.com" in href and len(href) > 30:
                    listing_url = href.split("?")[0]  # Strip query params
                    break
            # Fallback: first anchor
            if not listing_url and anchors:
                href = anchors[0].get_attribute("href") or ""
                if href.startswith("http"):
                    listing_url = href
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        url_hash = _url_hash(listing_url or f"{city}-{bhk}-{actual_rent}-{area_sqft}")

        return {
            "title":       title[:200],
            "location":    location[:200],
            "city":        city,
            "bhk":         bhk,
            "area_sqft":   area_sqft,
            "furnishing":  "Semi-Furnished",  # detail page needed for exact value
            "bathrooms":   min(bhk, 3),
            "actual_rent": actual_rent,
            "listing_url": listing_url,
            "url_hash":    url_hash,
            "source":      "scraped",          # ← marks as real scraped data
            "scraped_at":  datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.debug(f"Card parse error: {e}")
        return None


def _is_real_url(url: str | None) -> bool:
    """True if the URL is a real external listing page."""
    if not url:
        return False
    fake_patterns = ["mock", "demo", "rentwiz.app", "example.com", "/demo-"]
    return not any(p in url for p in fake_patterns)


# ── Supabase save ────────────────────────────────────────────────────────────

def save_to_supabase(listings: list[dict]) -> int:
    """
    Score each listing with ML model and upsert to Supabase.
    Only saves listings with real URLs (source='scraped').
    """
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")

    import os
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not supabase_url or supabase_url == "https://your-project.supabase.co":
        logger.error("Supabase not configured — add SUPABASE_URL to backend/.env")
        return 0

    from supabase import create_client
    from app.services.prediction import predict_rent, load_model
    from app.services.deal_scorer import classify_deal, compute_deal_pct

    load_model()
    db = create_client(supabase_url, supabase_key)
    saved = 0

    for listing in listings:
        if not _is_real_url(listing.get("listing_url")):
            logger.warning(f"Skipping fake URL: {listing.get('listing_url')}")
            continue
        try:
            # Run real ML prediction
            predicted_rent = predict_rent(
                city=listing["city"],
                bhk=listing["bhk"],
                area_sqft=listing["area_sqft"],
                furnishing=listing.get("furnishing", "Semi-Furnished"),
                bathrooms=listing.get("bathrooms", 1),
            )
            deal_pct   = compute_deal_pct(predicted_rent, listing["actual_rent"])
            deal_label = classify_deal(predicted_rent - listing["actual_rent"])

            row = {
                "url_hash":       listing["url_hash"],
                "listing_url":    listing["listing_url"],
                "title":          listing.get("title", ""),
                "location":       listing.get("location", listing["city"]),
                "city":           listing["city"],
                "bhk":            listing["bhk"],
                "area_sqft":      listing["area_sqft"],
                "furnishing":     listing.get("furnishing", "Semi-Furnished"),
                "bathrooms":      listing.get("bathrooms", 1),
                "actual_rent":    listing["actual_rent"],
                "predicted_rent": predicted_rent,
                "deal_pct":       round(deal_pct, 2),
                "deal_label":     deal_label,
                "source":         "scraped",    # ← key field
            }

            db.table("scraped_listings").upsert(row, on_conflict="url_hash").execute()
            saved += 1
            logger.info(
                f"  Saved: {listing['location']} | "
                f"actual ₹{listing['actual_rent']:,} | "
                f"predicted ₹{predicted_rent:,} | "
                f"{deal_label}"
            )

        except Exception as e:
            logger.error(f"DB save error: {e}")
            continue

    logger.info(f"Saved {saved}/{len(listings)} listings to Supabase (source=scraped)")
    return saved


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RentWiz MagicBricks Scraper")
    parser.add_argument("--city",        default="Mumbai",   help="City to scrape")
    parser.add_argument("--bhk",  type=int, default=2,       help="BHK type")
    parser.add_argument("--max",  type=int, default=30,      help="Max listings per run")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--save",        action="store_true", help="Save results to Supabase")
    args = parser.parse_args()

    results = scrape_magicbricks(
        city=args.city,
        bhk=args.bhk,
        max_listings=args.max,
        headless=not args.no_headless,
    )

    print(f"\n{'-'*65}")
    print(f"  Results: {len(results)} real listings for {args.bhk}BHK in {args.city}")
    print(f"{'-'*65}")
    for r in results[:10]:
        url_display = (r["listing_url"] or "NO URL")[:50]
        print(f"  {r['location']:<20} Rs. {r['actual_rent']:>8,}  {r['area_sqft']:>5} sqft  {url_display}")

    if len(results) > 10:
        print(f"  ... and {len(results)-10} more")

    if not results:
        print("\n  No real listings scraped. Possible reasons:")
        print("  - MagicBricks blocked the request")
        print("  - Run with --no-headless to debug")
        print("  - Check Chrome/ChromeDriver is installed")

    if args.save and results:
        saved = save_to_supabase(results)
        print(f"\n  Saved {saved} listings to Supabase (source='scraped')")
