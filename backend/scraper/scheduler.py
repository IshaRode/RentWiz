"""
RentWiz – Scraper Scheduler
Runs the MagicBricks scraper on a configurable interval using APScheduler.

Usage:
    cd backend
    python scraper/scheduler.py

Defaults to scraping top 6 Indian cities every 6 hours.
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper.magicbricks_scraper import scrape_magicbricks, save_to_supabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Scrape config – city + BHK combos to collect
SCRAPE_TARGETS = [
    {"city": "Mumbai",    "bhk": 1, "max": 15},
    {"city": "Mumbai",    "bhk": 2, "max": 20},
    {"city": "Mumbai",    "bhk": 3, "max": 15},
    {"city": "Delhi",     "bhk": 2, "max": 20},
    {"city": "Bangalore", "bhk": 2, "max": 20},
    {"city": "Hyderabad", "bhk": 2, "max": 15},
    {"city": "Pune",      "bhk": 2, "max": 15},
    {"city": "Chennai",   "bhk": 2, "max": 10},
]

INTERVAL_HOURS = 6   # Scrape every 6 hours


def run_scrape_job():
    """Execute one full scraping cycle across all targets."""
    logger.info("🚀 Scrape job started")
    total_scraped = 0
    total_saved = 0

    for target in SCRAPE_TARGETS:
        try:
            logger.info(f"  Scraping {target['bhk']}BHK in {target['city']}…")
            listings = scrape_magicbricks(
                city=target["city"],
                bhk=target["bhk"],
                max_listings=target["max"],
                headless=True,
            )
            saved = save_to_supabase(listings)
            total_scraped += len(listings)
            total_saved += saved
            logger.info(f"  ✅ {target['city']} {target['bhk']}BHK: {len(listings)} scraped, {saved} saved")
        except Exception as e:
            logger.error(f"  ❌ Failed {target['city']} {target['bhk']}BHK: {e}")

    logger.info(f"✅ Scrape cycle complete: {total_scraped} scraped, {total_saved} saved to DB")


if __name__ == "__main__":
    logger.info(f"⏰ Scheduler starting – interval: {INTERVAL_HOURS}h")
    logger.info(f"   Targets: {len(SCRAPE_TARGETS)} city/BHK combos")

    # Run immediately on start
    run_scrape_job()

    # Then schedule
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_scrape_job,
        trigger=IntervalTrigger(hours=INTERVAL_HOURS),
        id="scrape_job",
        name="MagicBricks Scraper",
        max_instances=1,       # prevent overlap
        coalesce=True,         # merge missed runs
    )

    logger.info(f"⏰ Next run in {INTERVAL_HOURS} hours. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
