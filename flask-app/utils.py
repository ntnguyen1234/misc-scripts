import json
import urllib.request


def load_text(file_path) -> str:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return fr.read().strip()
    
def write_text(data, file_path):
    with open(file_path, 'w', encoding='utf-8', errors='surrogateescape') as fw:
        fw.write(data.strip())

def request_url(url: str):
    req = urllib.request.Request(url, method='GET')

    with urllib.request.urlopen(req) as response:
        data = response.read()

    return json.loads(data)