import json
import time

from config import sub_reddit_group, headers
import requests

num_headers = len(headers)

with open('data/skeleton/skeleton3.json', 'r') as json_data:
    data_skeleton = json.load(json_data)
    json_data.close()

for subreddit in data_skeleton:

    sreddit = subreddit["subreddit"]
    topics = subreddit["topics"]
    sreddit_json_file = 'data/raw/{}.json'.format(sreddit)

    with open(sreddit_json_file, 'r') as fp:
        sreddit_current_data = json.load(fp)
        fp.close()

    num_topics = len(topics)
    i = 0
    h = i % num_headers

    tries = 0
    FOUND = False
    while i < num_topics:
        header = headers[h]
        url = topics[i] + ".json"
        if ("comments" not in url):
            i += 1
            continue

        if (len(sreddit_current_data) != 0) & (not FOUND):

            FOUND = True if topics[i] == sreddit_current_data[-1][0]["data"]["children"][0]["data"]["url"] else False
            i += 1
            continue

        resp = requests.get(url, headers=header)

        if (resp.status_code != 200) & (tries < num_headers):
            h = (h + 1) % num_headers
            tries += 1
            time.sleep(1)
            continue

        if (resp.status_code != 200) & (tries >= num_headers):
            print("fail to added, at {} header: {}".format(h, topics[i]))
            tries = 0
            i += 1
            h = i % num_headers

            # time.sleep(5)
            continue

        data = resp.json()

        assert len(data) == 2, "some abnormal responsed data"
        print("{}: successfully added, after {} tries: {}".format(i, tries, topics[i]))
        sreddit_current_data.append(data)
        i += 1
        h = i % num_headers
        tries = 0

        time.sleep(1)

        with open(sreddit_json_file, 'w') as f:
            json.dump(sreddit_current_data, f)
            f.close()
