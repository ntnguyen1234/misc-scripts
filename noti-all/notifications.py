import json
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import httpx
from bs4 import BeautifulSoup
from icecream import ic
from plyer import notification as noti

from utils import clean_split, load_json, load_text, uniques, write_text


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
        self.pastefy_headers = {
            'Authorization': f'Bearer {self.configs["pastefy_token"]}'
        }

    def test(self):
        with httpx.Client() as client:
            self.ntfy(
                client=client,
                message='Test',
                headers={'Title': 'Reddit inbox Test'},
                url=self.configs['reddit_url'],
            )

    def ntfy(
        self,
        client: httpx.Client,
        message: str,
        url: str = '',
        headers: dict[str, str] = {},
    ) -> httpx.Response:
        if not url:
            url = self.configs['notify_url']

        while True:
            try:
                response = client.post(
                    url=url, data=message.encode(encoding='utf-8'), headers=headers
                )
                ic(response.json())
                return response
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
            ):
                sleep(10)
                continue

    def reddit_inbox(
        self, client: httpx.Client, inbox_url: str, ids: set[str], notify_title: str
    ):
        try:
            response = client.get(inbox_url)
        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
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

            noti.notify(title=title, message=message_body[:256], timeout=20)

            link_title = data['link_title'] if 'link_title' in data else ''

            self.ntfy(
                client=client,
                message=f'{title}\n{message_body}\n---\n{link_title}\nhttps://old.reddit.com{data["context"]}',
                headers={'Title': notify_title},
                url=self.configs['reddit_url'],
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
                    notify_title='Reddit inbox',
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
                timeout=httpx.Timeout(30),
            ) as client:
                try:
                    response = client.get(url)
                except (
                    httpx.ConnectError,
                    httpx.ConnectTimeout,
                    httpx.ReadTimeout,
                    httpx.RemoteProtocolError,
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
                        'link': href,
                    }
                )
                ids.add(href)

            if not messages:
                sleep(60)
                continue

            with httpx.Client() as client:
                for message in messages:
                    text = f'{message["title"]}\n---\n{message["link"]}'

                    noti.notify(title='Github!', message=text[:254], timeout=30)

                    self.ntfy(client=client, message=text, headers={'Title': 'Github'})

            sleep(60)

    def pastefy_edit(self, idx: str, text: str):
        data = {
            'type': 'PASTE',
            'title': 'youtube-polymer.txt',
            'content': text,
        }

        with httpx.Client(headers=self.pastefy_headers) as client:
            response = client.put(url=f'{self.pastefy_url}/{idx}', data=data)
            ic(response.json())

    @staticmethod
    def youtube_polymer():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
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
            follow_redirects=True,
        ) as client:
            response = client.get('https://www.youtube.com')
            if response.status_code >= 300:
                print(response.content)

            yt_html = BeautifulSoup(response.content, 'lxml')
            Path('yt.html').write_bytes(response.content)

        href = yt_html.select_one(
            '[href*="/desktop_polymer"], [src*="/desktop_polymer"]'
        )['href']
        print(href)
        return href

    def add_polymer(self):
        idx = 'G1Txv5su'
        while True:
            # hrefs = list(load_text('polymer.txt', True))
            hrefs = []
            hrefs_full = []
            for line in load_text('polymer.txt', True):
                hrefs_full.append(line)
                hrefs.append(next(clean_split(line, '-')))

            try:
                if (href := self.youtube_polymer()) in hrefs:
                    sleep(300)
                    continue

                utc_time = datetime.now(timezone.utc).isoformat(sep=' ', timespec='minutes')
                
                hrefs.append(href)
                hrefs_full.append(f'{href} - {utc_time}')

                self.pastefy_edit(idx, '\n'.join(hrefs_full))
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
            ):
                print('Error!')
                sleep(60)
                continue

            write_text(hrefs_full, 'polymer.txt')

            noti.notify(
                title='Youtube polymer',
                message=href,
                timeout=30,
            )
            with httpx.Client() as client:
                self.ntfy(client=client, message=href, url=self.configs['polymer_url'])

            sleep(300)
