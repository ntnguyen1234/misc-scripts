import json
from pathlib import Path
from time import sleep

import httpx
from bs4 import BeautifulSoup
from icecream import ic
from plyer import notification as noti

from utils import load_json, load_text, uniques, write_text


class Notifications:
    def __init__(self):
        self.configs = load_json('config.json')
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/116.0',
        }
        # Pastefy
        self.pastefy_url = 'https://pastefy.app/api/v2/paste'
        self.pastefy_headers = { 'Authorization': f'Bearer {self.configs["pastefy_token"]}' }

    def ntfy(
            self, 
            client: httpx.Client, 
            message: str, 
            url: str = '',
            headers: dict[str, str] = {}
        ) -> httpx.Response:
        if not url:
            url = self.configs['notify_url']
        
        while True:
            try:
                response = client.post(
                    url=url,
                    data=message.encode(encoding='utf-8'),
                    headers=headers
                )
                ic(response.json())
                return response
            except (
                httpx.ConnectError, 
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError
            ):
                sleep(10)
                continue

    def reddit_inbox(
            self,
            client: httpx.Client,
            inbox_url: str,
            ids: set[str],
            notify_title: str
        ):
            try:
                response = client.get(inbox_url)
            except (
                httpx.ConnectError, 
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError
            ):
                sleep(10)
                return

            try:
                messages = response.json()
            except json.decoder.JSONDecodeError:
                print(response.content)
                sleep(10)
                return

            if 'data' not in messages:
                ic(messages)
                sleep(10)
                return
            
            for message in messages['data']['children']:
                data = message['data']

                if not data['new']:
                    continue
                
                if data['id'] in ids:
                    continue

                title = f'{data["subreddit_name_prefixed"]} - u/{data["author"]}'
                message_body: str = data['body']
                
                noti.notify(
                    title=title,
                    message=message_body[:256],
                    timeout=20
                )

                link_title = data['link_title'] if 'link_title' in data else ''

                self.ntfy(
                    client=client,
                    message=f'{title}\n{message_body}\n---\n{link_title}\nhttps://old.reddit.com{data["context"]}',
                    headers={ 'Title': notify_title }
                )
                ids.add(data['id'])

    def reddit_notify(self):
        ids = set()
        with httpx.Client() as client:
            while True:
                self.reddit_inbox(
                    client,
                    inbox_url=self.configs['reddit_inbox'],
                    ids=ids,
                    notify_title='Reddit inbox'
                )

                # sleep(5)

                # self.reddit_inbox(
                #     client,
                #     inbox_url=self.configs['reddit_mod'],
                #     ids=ids,
                #     notify_title='Reddit moderator'
                # )
                
                sleep(30)

    def github_notify(self):
        ids = set()
        url = 'https://github.com/notifications?query=is%3Aunread'
        
        while True:
            with httpx.Client(
                headers=self.headers,
                cookies=self.configs['cookies'],
                http2=True,
                follow_redirects=True,
                timeout=httpx.Timeout(30)
            ) as client:
                try:
                    response = client.get(url)
                except (
                    httpx.ConnectError, 
                    httpx.ConnectTimeout,
                    httpx.ReadTimeout,
                    httpx.RemoteProtocolError
                ):
                    print('Github Error!')
                    sleep(30)
                    continue

                Path('github.html').write_bytes(content := response.content)
            
            github_html = BeautifulSoup(content, 'lxml')
            if not (noti_links := github_html.select('a.notification-list-item-link')):
                sleep(60)
                continue

            messages = []
            for noti_link in noti_links:
                if (href := noti_link['href']) in ids:
                    continue
                
                messages.append(
                    {
                        'title': noti_link.select_one('p.markdown-title').text.strip(),
                        'link': href
                    }
                )
                ids.add(href)

            if not messages:
                sleep(60)
                continue

            with httpx.Client() as client:
                for message in messages:
                    text = f'{message["title"]}\n---\n{message["link"]}'

                    noti.notify(
                        title='Github!',
                        message = text[:256],
                        timeout=30
                    )
                    
                    self.ntfy(
                        client=client,
                        message=text,
                        headers={ 'Title': 'Github' }
                    )

            sleep(60)
    
    def pastefy_edit(self, idx: str, text: str):
        data = {
            'type': 'PASTE',
            'title': 'youtube-polymer.txt',
            'content': text,
        }
        
        with httpx.Client(headers=self.pastefy_headers) as client:
            response = client.put(
                url=f'{self.pastefy_url}/{idx}',
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
            Path('yt.html').write_bytes(response.content)

        hrefs = []
        for item in yt_html.select('[href*="_polymer_"], [src*="_polymer_"]'):
            if 'href' in item.attrs:
                hrefs.append(item['href'])
            else:
                hrefs.append(item['src'])

        return uniques(hrefs)
    
    def add_polymer(self):
        idx = 'G1Txv5su'
        while True:
            hrefs = list(load_text('polymer.txt', True))

            try:
                if not (polymer_urls := self.youtube_polymer()):
                    noti.notify(
                        title='Youtube polymer',
                        message='No HREF!',
                        timeout=30
                    )
                    print('No HREF!')
                    sleep(60)
                    continue
                
                new_urls = [polymer_url for polymer_url in polymer_urls if polymer_url not in hrefs]
                if not new_urls:
                    sleep(300)
                    continue

                hrefs.extend(new_urls)
                self.pastefy_edit(idx, '\n'.join(hrefs))
            except (
                httpx.ConnectError, 
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError
            ):
                print('Error!')
                sleep(60)
                continue

            write_text(hrefs, 'polymer.txt')

            noti.notify(
                title='Youtube polymer',
                message=(message := '\n'.join(new_urls)),
                timeout=30
            )
            with httpx.Client() as client:
                self.ntfy(
                    client=client, 
                    message=message,
                    url=self.configs['polymer_url']
                )

            sleep(300)