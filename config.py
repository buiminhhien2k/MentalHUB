import os
from dotenv import load_dotenv

load_dotenv()

sub_reddit_group = [
    {
        "type": "Bipolar Disoder",
        "subreddits": ["bipolar", "BipolarReddit", "BipolarSOs"]
    },
    {
        "type": "Depression",
        "subreddits": ["depression", "depression_help", "AnxietyDepression"]
    },
    {
        "type": "Anxiety",
        "subreddits": ["socialanxiety", "Anxietyhelp", "Anxiety"]
    },
    {
        "type": "PTSD",
        "subreddits": ["ptsd", "ptsdrecovery", "CPTSD"]
    },
    {
        "type": "OCD",
        "subreddits": ["OCD", "OCDRecovery", "HOCD"]
    },
    {
        "type": "Eating Disorders",
        "subreddits": ["EatingDisorders", "EDAnonymous", 'fuckeatingdisorders', "BingeEatingDisorder"]
    },
    {
        "type": "ADHD",
        "subreddits": ["ADHD", "adhdwomen", "ADHD_partners"]
    }
]

reddit_sub_reddits = [
    "bipolar",
    "depression",
    "socialanxiety",
    "ptsd",
    "OCD",
    "EatingDisorders",
    "ADHD"
]


subreddit_link_format = "https://www.reddit.com/r/{}"
cleandatapath = "../data/clean/clean_data.json"

num_topics_per_subreddits = 1200

headers = [
    # guest profile
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': os.getenv('GUEST_HEADER_COOKIE'),
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    },
    # 2nd profile
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': os.getenv('SECOND_HEADER_COOKIE'),
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    },
    # incognito header
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': os.getenv('INCOGNITO_HEADER_COOKIE'),
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    },
    # normal header
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': os.getenv('NORMAL_HEADER_COOKIE'),
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    },
    # empty header
    {}
]

PORT = int(os.getenv("PORT"))

DOC_ID_COMMENTS_MAPPER_ID = os.getenv("DOC_ID_COMMENTS_MAPPER_ID")
SUMMERIZER_ID = os.getenv("SUMMERIZER_ID")
MATRIX_ID = os.getenv("MATRIX_ID")
EMBEDDER_ID = os.getenv("EMBEDDER_ID")
CLASSIFIER_ID = os.getenv("CLASSIFIER_ID")
