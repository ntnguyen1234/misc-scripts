import json
from subprocess import run
from time import sleep


def main():
    with open('data.json', 'r') as fr:
        data = json.load(fr)

    browser_path = data['browser_path']

    base_urls = [
        'https://transparencyreport.google.com/safe-browsing/search?url=',
        'https://safeweb.norton.com/report/show?url=',
        'https://sitecheck.sucuri.net/results/',
        'https://www.siteadvisor.com/sitereport.html?url=',
    ]
    base_domains = [
        'https://otx.alienvault.com/indicator/domain/',
        'https://opentip.kaspersky.com/',
        'https://www.virustotal.com/gui/domain/',
        'https://transparencyreport.google.com/safe-browsing/search?url=',
        'https://safeweb.norton.com/report/show?url=',
        'https://sitecheck.sucuri.net/results/',
        'https://www.siteadvisor.com/sitereport.html?url=',
        'https://www.urlvoid.com/scan/',
        'https://yandex.com/safety/?l10n=en&url='
    ]
    test_url = input('>>> ')
    for url in base_urls:
        new_url = f'{url}{test_url}'
        print(new_url)
        run([
            'powershell', 
            '&', f'"{browser_path}"'
            '-p', data['profile'], # For Firefox
            f'"{new_url}"'
        ])
        sleep(1)

    test_domain = test_url.split('://')[1].split('/')[0].replace('www.', '')
    for domain in base_domains:
        new_domain = f'{domain}{test_domain}'
        print(new_domain)
        run([
            'powershell', 
            '&', f'"{browser_path}"'
            '-p', data['profile'], # For Firefox
            f'"{new_domain}"'
        ])
        sleep(1)


if __name__ == "__main__":
    main()