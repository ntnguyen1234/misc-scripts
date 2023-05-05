from pathlib import Path

from httpx import Client
from PIL import ImageGrab
from pyclip import copy


def upload(file):
    with open(file, 'rb') as f:
        with Client() as client:
            response = client.post(url='https://ttm.sh', files={'file': f})
            copy(url := response.text.strip())
            print(url)


def main():
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
        
    input('...')


if __name__ == "__main__":
    main()