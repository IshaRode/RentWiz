"""
Batch scraper — runs MagicBricks for all cities we don't have scraped data for yet.
"""
import subprocess
import sys
from pathlib import Path

CITIES = [
    ("Delhi",     2),
    ("Delhi",     3),
    ("Hyderabad", 2),
    ("Hyderabad", 3),
    ("Chennai",   2),
    ("Pune",      2),
    ("Kolkata",   2),
    ("Ahmedabad", 2),
]

python = str(Path(sys.executable))

for city, bhk in CITIES:
    print(f"\n{'='*60}")
    print(f"  Scraping {bhk}BHK in {city}...")
    print(f"{'='*60}")
    result = subprocess.run(
        [python, "scraper/magicbricks_scraper.py",
         "--city", city, "--bhk", str(bhk), "--max", "20", "--save"],
        cwd=Path(__file__).parent.parent,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  Warning: scraper exited with code {result.returncode} for {city} {bhk}BHK")

print("\nBatch scraping complete!")
