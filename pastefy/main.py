from pathlib import Path
import httpx

from pastefy_app import Pastefy


def main():
    text_id = 'G1Txv5su'

    app = Pastefy()
    # app.edit(text_id)
    # app.youtube_polymer(text_id)
    app.add_polymer(text_id)

    # cookies = {
    #     'logged_in': 'yes',
    #     'user_session': 'jxyE_lZCqmmp1vIEO24EHp7tkVXEN6YgMO56Ck7m3T3Pjlbb',
    #     'dotcom_user': 'stephenhawk8054',
    #     'fileTreeExpanded': 'false',
    #     'has_recent_activity': '1',
    # }

    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Cache-Control': 'no-cache',
    #     'Connection': 'keep-alive',
    #     'Pragma': 'no-cache',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'cross-site',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/116.0',
    # }

    # params = {
    #     'query': 'is:unread',
    # }

    # url = 'https://github.com/notifications'

    # with httpx.Client(
    #     headers=headers,
    #     cookies=cookies,
    #     http2=True,
    #     follow_redirects=True,
    #     timeout=httpx.Timeout(30)
    # ) as client:
    #     response = client.get(url, params=params)

    # Path('github.html').write_bytes(response.content)


if __name__ == "__main__":
    main()