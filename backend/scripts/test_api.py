import urllib.request
import json

def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

# Test /best-deals
print("=== /best-deals (Supabase) ===")
data = get("http://localhost:8000/api/v1/best-deals?city=Bangalore&limit=3")
print("Source:", data.get("filters_applied", {}).get("source", "unknown"))
print("Total:", data["total"])
for l in data["listings"]:
    print(" ", l["deal_label"], "|", l["city"], "| actual", l["actual_rent"], "| predicted", l["predicted_rent"], "| score", l["deal_score"])

print()
print("=== /area-insights (Supabase) ===")
ins = get("http://localhost:8000/api/v1/area-insights?city=Delhi")
print("City:", ins["city"])
print("Total listings:", ins["total_listings"])
print("Avg rent:", ins["avg_rent"])
print("Deal distribution:", ins["deal_distribution"])
print("BHK breakdown:", ins["rent_by_bhk"])
