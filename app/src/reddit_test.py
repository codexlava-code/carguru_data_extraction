import praw
import pandas as pd
from datetime import datetime, timedelta, timezone

import requests
from prawcore import Requestor, Session
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from praw import Reddit


class MyRequestor(Requestor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = create_urllib3_context()
        self._http = requests.Session()
        adapter = HTTPAdapter()
        self._http.mount("https://", adapter)

reddit = praw.Reddit(
    client_id="WV3lFjhgPCoOUZhbwWMySQ",
    client_secret="QeeciQJv3hjIQaush4BLy4aKOZJbYQ",
    user_agent="Mozilla/5.0 RedditScraper/1.0",
    requestor_class=MyRequestor,  # pass the class, NOT an instance
    read_only=True
)

print(reddit.read_only)



response = requests.get("https://www.reddit.com", headers={"User-Agent": "Mozilla/5.0"})
print(response.status_code)

# Calculate timestamp for 2 years ago
two_years_ago = datetime.now(timezone.utc) - timedelta(days=2 * 365)

# Keywords to search
search_query = "best places to live in the UK"

# Use selected subreddits or 'all'
subreddit = reddit.subreddit("all")

results = []

# Search using Reddit's built-in search (can be slow)
for submission in subreddit.search(search_query, sort="comments", limit=1000, time_filter="all"):
    created_utc = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
    if created_utc < two_years_ago:
        continue
    if submission.num_comments >= 50:
        results.append({
            "title": submission.title,
            "subreddit": submission.subreddit.display_name,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "created_utc": created_utc.strftime('%Y-%m-%d'),
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}",
        })

print(f"Collected {len(results)} posts")

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("reddit_best_places_to_live_UK.csv", index=False)
print("Saved to reddit_best_places_to_live_UK.csv")
