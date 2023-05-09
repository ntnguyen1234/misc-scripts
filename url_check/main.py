from pyclip import copy


def main():
    urls = [
        'https://otx.alienvault.com/indicator/domain/',
        'https://safeweb.norton.com/report/show?url=',
        'https://sitecheck.sucuri.net/results/',
        'https://www.siteadvisor.com/sitereport.html?url=',
        'https://www.urlvoid.com/scan/'
    ]
    domain = input('>>> ')
    dom_urls = [f'{url}{domain}' for url in urls]
    copy('\n'.join(dom_urls))

    input('...')


if __name__ == "__main__":
    main()