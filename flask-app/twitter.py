import json
import urllib.request
from urllib.parse import urlparse, urlunparse

from utils import request_url


def get_tweet(url: str):
    parsed = urlparse(url)
    replaced = parsed._replace(netloc='api.vxtwitter.com')

    new_url = urlunparse(replaced)

    data = request_url(new_url)
    with open('data.json', 'w', encoding='utf-8') as fw:
        json.dump(data, fw)