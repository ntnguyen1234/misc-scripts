import ssl

import httpx
from icecream import ic


class Pastefy:
    def __init__(self, configs: dict) -> None:
        self.configs = configs
        
        # Pastefy
        self.pastefy_url = 'https://pastefy.app/api/v2/paste'
        self.pastefy_headers = {
            'Authorization': f'Bearer {self.configs["pastefy_token"]}'
        }

    def get_pastefy(self):
        with httpx.Client() as client:
            response = client.get(f'https://pastefy.app/{self.configs["pastefy_id"]}/raw')
            return response.json()

    def pastefy_edit(self, text: str):
        idx = self.configs['pastefy_id']
        data = {
            'type': 'PASTE',
            'title': 'cf-tunnels.json',
            'content': text,
        }

        with httpx.Client(
            headers=self.pastefy_headers, verify=ssl.create_default_context()
        ) as client:
            response = client.put(url=f'{self.pastefy_url}/{idx}', data=data)
            ic(response.json())