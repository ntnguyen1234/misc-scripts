from subprocess import run
from time import sleep


def main():
    urls = [
        'https://otx.alienvault.com/indicator/domain/',
        'https://safeweb.norton.com/report/show?url=',
        'https://sitecheck.sucuri.net/results/',
        'https://www.siteadvisor.com/sitereport.html?url=',
        'https://www.urlvoid.com/scan/'
    ]
    domain = input('>>> ')
    for url in urls:
        new_url = f'{url}{domain}'
        print(new_url)
        run(['powershell', f'start "{new_url}"'])
        sleep(1)


if __name__ == "__main__":
    main()