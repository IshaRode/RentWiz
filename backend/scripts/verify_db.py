from dotenv import load_dotenv
load_dotenv('.env')
import os
from supabase import create_client

db = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

total = db.table('scraped_listings').select('id', count='exact').execute()
print('Total listings:', total.count)

good = db.table('scraped_listings').select('id', count='exact').eq('deal_label','good_deal').execute()
fair = db.table('scraped_listings').select('id', count='exact').eq('deal_label','fair').execute()
over = db.table('scraped_listings').select('id', count='exact').eq('deal_label','overpriced').execute()
print('Good deals:', good.count, '| Fair:', fair.count, '| Overpriced:', over.count)

top = db.table('scraped_listings').select('title,city,actual_rent,predicted_rent,deal_score,deal_label').order('deal_score', desc=True).limit(5).execute()
print('\nTop 5 deals from Supabase:')
for r in top.data:
    label     = r['deal_label']
    city      = r['city']
    actual    = r['actual_rent']
    predicted = r['predicted_rent']
    score     = r['deal_score']
    print(label, '|', city, '| actual', actual, '| predicted', predicted, '| score', score)
