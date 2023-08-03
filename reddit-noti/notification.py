import json
from time import sleep

import httpx
from icecream import ic

from utils_reddit import load_json, write_json


class Notification:
    def __init__(self, config: dict[str, str]):
        self.config = config

    def notify(self, message: str):
        # message = 'Test'
        
        with httpx.Client() as client:
            response = client.post(self.config['notify_url'], data=message.encode(encoding='utf-8'))
            ic(response.json())

    def get_noti(self):
        ids = set()
        with httpx.Client() as client:
            while True:
                try:
                    response = client.get(self.config['reddit_inbox'])
                except (
                    httpx.ConnectError, 
                    httpx.ConnectTimeout,
                    httpx.ReadTimeout
                ):
                    sleep(10)
                    continue
                
                # write_json(response.json(), 'example.json')
                # messages = load_json('example.json')

                try:
                    messages = response.json()
                except json.decoder.JSONDecodeError:
                    print(response.content)
                    sleep(10)
                    continue
                
                for message in messages['data']['children']:
                    data = message['data']

                    if not data['new']:
                        continue
                    
                    if data['id'] in ids:
                        continue

                    noti_message = f'{data["subreddit_name_prefixed"]} - u/{data["author"]}\n{data["body"]}\n---\n{data["link_title"]}\nhttps://old.reddit.com{data["context"]}'

                    self.notify(noti_message)
                    ids.add(data['id'])
                
                sleep(30)