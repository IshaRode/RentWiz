"""
Shows top 5 deals from the API and confirms whether they're from scraped or seeded data.
"""
import urllib.request, json

data = json.loads(urllib.request.urlopen("http://localhost:8000/api/v1/best-deals?limit=10").read())

print("Source:", data["filters_applied"]["source"])
print("Total:", data["total"])
print()
for i, l in enumerate(data["listings"], 1):
    url = l.get("listing_url") or "NO URL"
    is_scraped = "magicbricks.com" in url
    flag = "REAL" if is_scraped else "seeded"
    print(f"[{i}] {flag:6} | {l['city']:12} | {l['deal_label']:10} | actual {l['actual_rent']:>8,} | predicted {l['predicted_rent']:>8,} | score {l['deal_score']:>8,}")
    print(f"       {l['title']}")
    print(f"       {url[:80]}")
    print()
