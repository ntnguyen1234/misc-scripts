from time import sleep

import httpx
from bs4 import BeautifulSoup
from icecream import ic
from notification import Notification
from plyer import notification as noti

from utils import load_json, load_text


class Pastefy:
    def __init__(self) -> None:
        self.token = str(load_text('tokens.txt'))
        self.base_url = 'https://pastefy.app/api/v2/paste'
        self.headers = {
            'Authorization': f'Bearer {self.token}'
        }
        self.notifier = Notification(load_json('config.json'))
    
    def edit(self, idx: str, text: str):
        data = {
            'type': 'PASTE',
            'title': 'youtube-polymer.txt',
            'content': text,
        }
        
        with httpx.Client(headers=self.headers) as client:
            response = client.put(
                url=f'{self.base_url}/{idx}',
                data=data
            )
            ic(response.json())


    @staticmethod
    def youtube_polymer():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        with httpx.Client(
            headers=headers,
            http2=True,
            timeout=httpx.Timeout(30),
            follow_redirects=True
        ) as client:
            response = client.get('https://www.youtube.com')
            if response.status_code >= 300:
                print(response.content)

            yt_html = BeautifulSoup(response.content, 'lxml')
        #     Path('yt.html').write_bytes(response.content)
        # yt_html = BeautifulSoup(str(load_text('yt.html')), 'lxml')

        return yt_html.select_one('link[as="script"][href*="polymer_"]')['href']
    

    def add_polymer(self, idx: str):
        while True:
            url = f'https://pastefy.app/{idx}/raw'

            try:
                with httpx.Client() as client:
                    hrefs = client.get(url).text.strip().split()

                if not (href := self.youtube_polymer()):
                    noti.notify(
                        title='Youtube polymer',
                        message='No HREF!',
                        timeout=30
                    )
                    self.notifier.notify('Youtube polymer\n---\nNo HREF!')
                    sleep(60)
                    continue

                if href in hrefs:
                    sleep(300)
                    continue

                hrefs.append(href)
                self.edit(idx, '\n'.join(hrefs))
            except (
                httpx.ConnectError, 
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError
            ):
                sleep(60)
                continue

            noti.notify(
                title='Youtube polymer',
                message=href,
                timeout=30
            )
            self.notifier.notify(f'Youtube polymer\n---\n{href}')
            sleep(300)