import random
import string
from base64 import urlsafe_b64encode
from datetime import datetime
from pathlib import Path

from httpx import Client
from PIL import ImageGrab
from pyclip import copy, paste


def upload(file):
    with open(file, 'rb') as f:
        with Client() as client:
            response = client.post(url='https://0x0.st', files={'file': f})
            copy(url := response.text.strip())
            print(url)


def upload_file(file_name: str, fr: bytes):
    api_key = 'a3a1021917199453120b94c32b9aa8f6'
    headers = {'Authorization': f'Bearer {api_key}'}

    with Client(headers=headers) as client:
        response = client.post(
            url='https://neocities.org/api/upload',
            files={file_name: fr}
        )
        if response.status_code == 200:
            copy(export_url := f'https://sh-files.neocities.org/{file_name}')
            print(export_url)


def main():
    upload_type = input('>>> ')

    if upload_type == 'img':
        img = ImageGrab.grabclipboard()
        
        if isinstance(img, list):
            if not isinstance(img[0], str):
                return
            upload(img[0])
        else:
            temp_file = Path('.') / f'temp.{img.format.lower()}'
            img.save(temp_file)
            upload(temp_file)
        temp_file.unlink()
    else:
        characters = string.ascii_letters + string.digits
        current_time = datetime.now().strftime('%m%d')
        temp = ''.join([random.choice(characters) for _ in range(4)]) + (
            urlsafe_b64encode(bytes(current_time, encoding='utf-8'))
            .decode(encoding='utf-8')
            .replace('=', '')
        )

        if ':' not in upload_type:
            file_name = f'{temp}.{upload_type}'
            upload_file(file_name, paste())
        else:
            file_name = f'{temp}{Path(upload_type).suffix}'
            with open(upload_type, 'rb') as fr:
                upload_file(file_name, fr)
        
    input('...')


if __name__ == "__main__":
    # test 4
    main()