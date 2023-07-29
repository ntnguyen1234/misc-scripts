from time import sleep
from httpx import Client
from icecream import ic
from utils_reddit import load_json, write_json


class Notification:
    def __init__(self, config: dict[str, str]):
        self.config = config

    def notify(self, message: str):
        # message = 'Test'
        
        with Client() as client:
            response = client.post(self.config['notify_url'], data=message.encode(encoding='utf-8'))
            ic(response.content)

    def get_noti(self):
        ids = set()
        with Client() as client:
            while True:
                response = client.get(self.config['reddit_inbox'])
                messages = response.json()
                
                # write_json(response.json(), 'example.json')
                # messages = load_json('example.json')

                for message in messages['data']['children']:
                    data = message['data']

                    if not data['new']:
                        continue
                    
                    if data['id'] in ids:
                        continue

                    noti_message = f'{data["subreddit_name_prefixed"]} - {data["author"]}\n{data["link_title"]}\n---\n{data["body"]}\n---\nhttps://old.reddit.com{data["context"]}'

                    self.notify(noti_message)
                    ids.add(data['id'])
                
                sleep(30)