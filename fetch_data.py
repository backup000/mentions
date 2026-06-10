import os
import json
import requests
from datetime import datetime, timedelta

# 1. Authenticate with Reddit API
# These secrets will be safely injected by GitHub Actions
client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
user_agent = "script:hyrox_tracker:v1.0 (by /u/misnomerx)"

auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
data = {'grant_type': 'client_credentials'}
headers = {'User-Agent': user_agent}

res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
print("REDDIT RESPONSE:", res.text) # <-- This prints the exact error from Reddit to the logs
TOKEN = res.json()['access_token']
headers['Authorization'] = f'bearer {TOKEN}'

# 2. Function to count keyword mentions in r/hyrox
def get_mentions(keyword):
    # Searches posts and comments from the past month
    url = f"https://oauth.reddit.com/r/hyrox/search?q={keyword}&restrict_sr=1&sort=new&t=month&limit=100"
    response = requests.get(url, headers=headers).json()
    
    count = 0
    positive = 0
    neutral = 0
    negative = 0
    
    if 'data' in response and 'children' in response['data']:
        for post in response['data']['children']:
            count += 1
            text = (post['data'].get('title', '') + " " + post['data'].get('selftext', '')).lower()
            
            # Simple keyword-based sentiment rules
            if any(w in text for w in ['great', 'love', 'perfect', 'best', 'accurate', 'upgrade']):
                positive += 1
            elif any(w in text for w in ['bad', 'issue', 'broken', 'fail', 'returned', 'poor', 'hate']):
                negative += 1
            else:
                neutral += 1
                
    return {"total": count, "sentiment": {"positive": positive, "neutral": neutral, "negative": negative}}

# 3. Fetch data for both brands
garmin_results = get_mentions("garmin")
amazfit_results = get_mentions("amazfit")

# 4. Save to a JSON file for our website to read
output_data = {
    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "garmin": garmin_results,
    "amazfit": amazfit_results
}

with open('data.json', 'w') as f:
    json.dump(output_data, f, indent=4)

print("Data successfully updated!")
