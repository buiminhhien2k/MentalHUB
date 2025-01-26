from config import sub_reddit_group, cleandatapath
import json

datapathformat = "../data/raw/{}.json"

post_records_list = list()

post_records_name_set = set()

for group in sub_reddit_group:
    type = group["type"]
    subreddits_list = group["subreddits"]
    # get all subreddit files
    for subreddit in subreddits_list:

        datapath = datapathformat.format(subreddit)
        with open(datapath, 'r') as json_data:
            print(datapath)
            data = json.load(json_data)

            # sample, put into for loop later
            post_set = set()
            for record in data:

                # post information
                post_title = record[0]["data"]["children"][0]["data"]["title"]
                post_content = record[0]["data"]["children"][0]["data"]["selftext"]
                post_created_utc = record[0]["data"]["children"][0]["data"]["created_utc"]
                post_author = record[0]["data"]["children"][0]["data"]["author"]
                post_score = record[0]["data"]["children"][0]["data"]["score"]

                post_name_id = record[0]["data"]["children"][0]["data"]["name"]
                if (post_content == '[deleted]' or post_content == '[removed]'): continue
                if (post_author == "AutoModerator"): continue

                comments_list = list()
                # traverse through comments (only the first level)
                if (len(record) == 1):
                    print("found abnormal")
                    continue
                for comments_first_level in record[1]["data"]["children"]:
                    if comments_first_level["kind"] == "more":
                        continue
                    if comments_first_level["data"]["author"] == "AutoModerator":
                        continue


                    # get the comments basic information
                    comment_content = comments_first_level["data"]["body"]
                    comment_created_utc = comments_first_level["data"]["created_utc"]
                    comment_author = comments_first_level["data"]["author"]
                    comment_score = comments_first_level["data"]["score"]

                    # append the valid comments to the comments_list
                    comments_list.append({
                        "comment_content": comment_content,
                        "comment_created_utc": comment_created_utc,
                        "comment_author": comment_author,
                        "comment_score": comment_score
                    })

                # if no comment found, skip this post
                # if len(comments_list) == 0: continue

                # if post_name_id in post_records_name_set:
                #     continue
                #
                # post_records_name_set.add(post_name_id)


                post_records_list.append({
                    "group": type,
                    "subreddit": subreddit,

                    "post_title": post_title,
                    "post_content": post_content,
                    "post_created_utc": post_created_utc,
                    "post_author": post_author,
                    "post_score": post_score,

                    "comments_list": comments_list
                })
            # print(record)

            json_data.close()

print(len(post_records_list))

with open(cleandatapath, 'w') as f:
    json.dump(post_records_list, f)
    f.close()
