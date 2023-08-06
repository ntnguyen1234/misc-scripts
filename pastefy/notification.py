import httpx
from icecream import ic


class Notification:
    def __init__(self, config: dict[str, str]):
        self.config = config

    def notify(self, message: str):
        # message = 'Test'
        
        with httpx.Client() as client:
            response = client.post(self.config['notify_url'], data=message.encode(encoding='utf-8'))
            ic(response.json())