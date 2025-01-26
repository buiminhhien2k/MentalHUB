import time
import json
from config import reddit_sub_reddits, subreddit_link_format, headers, num_topics_per_subreddits
import requests
num_headers = len(headers)

list_of_sub_reddits = list()

for k, sub_reddit in enumerate(reddit_sub_reddits):
    subreddit_url = subreddit_link_format.format(sub_reddit) + ".json"
    header = headers[k % num_headers]

    after = None
    i = 0

    set_of_topics = set()
    while i < (num_topics_per_subreddits // 25):
        url = subreddit_url
        if after:
            url += "?after={}".format(after)
        resp = requests.get(url, headers=header)
        print(resp.status_code)
        if resp.status_code != 200:
            header = headers[(k+1) % num_headers]
            continue
        data = resp.json()
        i += 1

        after = data["data"]["after"]
        children = data["data"]["children"]
        for child in children:
            if (sub_reddit in child["data"]["url"]):
                set_of_topics.add(child["data"]["url"])
    print(f"subreddit {sub_reddit} collects {len(set_of_topics)} topics")
    list_of_sub_reddits.append(

            {
                "subreddit": sub_reddit,
                "topics": list(set_of_topics)
            }

    )

with open('../data/skeleton/skeleton4.json', 'w') as f:
    json.dump(list_of_sub_reddits, f)
