"""
Cleanup script: remove scraped listings with clearly wrong rents (< Rs. 5,000)
then re-run the scraper for Bangalore with the fixed parser.
"""
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent.parent / ".env")
from supabase import create_client

db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

# Find bad rows
bad = (
    db.table("scraped_listings")
    .select("id, title, actual_rent, city, listing_url")
    .lt("actual_rent", 5000)
    .execute()
)
print(f"Found {len(bad.data)} listings with actual_rent < Rs.5000:")
for r in bad.data:
    print(f"  {r['city']} | {r['title']} | Rs.{r['actual_rent']}")

if bad.data:
    ids = [r["id"] for r in bad.data]
    db.table("scraped_listings").delete().in_("id", ids).execute()
    print(f"Deleted {len(ids)} bad listings.")
else:
    print("Nothing to clean up.")

# Verify
total = db.table("scraped_listings").select("id", count="exact").execute()
scraped = [
    r for r in db.table("scraped_listings").select("listing_url, actual_rent").execute().data
    if "rentwiz.app" not in (r.get("listing_url") or "")
    and "example.com" not in (r.get("listing_url") or "")
]
print(f"\nTotal rows: {total.count} | Scraped with real URLs: {len(scraped)}")
