import io
import random
import string
from pathlib import Path

from b2sdk import v2 as b2
from PIL import ImageGrab
from pyclip import copy, paste


class B2:
    def __init__(self, b2_keys: dict[str, str]):
        self.info = b2.InMemoryAccountInfo()
        self.b2_api = b2.B2Api(self.info)

        self.b2_keys = b2_keys
    
    def authorize(self):
        self.b2_api.authorize_account('production', self.b2_keys['keyID'], self.b2_keys['applicationKey'])
        self.bucket = self.b2_api.get_bucket_by_name(self.b2_keys['bucketName'])

    def upload_image(self, b2_file_name: str) -> str | None:
        img = ImageGrab.grabclipboard()
                
        if isinstance(img, list):
            if not isinstance(img[0], str):
                return
            
            if (suffix := Path(img[0]).suffix).strip('.') not in self.b2_keys['imgTypes']:
                return

            self.bucket.upload_local_file(
                local_file=img[0],
                file_name=(file_name := b2_file_name+suffix),
            )
        else:
            if (img_format := img.format).lower() not in self.b2_keys['imgTypes']:
                return

            img_bytes = io.BytesIO()
            img.save(img_bytes, format=img_format)
            img_bytes = img_bytes.getvalue()

            self.bucket.upload_bytes(
                data_bytes=img_bytes,
                file_name=(file_name := f'{b2_file_name}.{img_format.lower()}')
            )

        return file_name
    
    def upload_text(self, b2_file_name: str, upload_type: str, local_file: str=None) -> str:
        file_name = f'{b2_file_name}.{upload_type.lower()}'
        
        if local_file:
            self.bucket.upload_local_file(
                local_file=local_file,
                file_name=file_name
            )
        else:
            self.bucket.upload_bytes(
                data_bytes=paste(),
                file_name=file_name
            )
            
        return file_name
    
    def upload_from_clipboard(self, upload_type: str):
        characters = string.ascii_letters + string.digits
        b2_file_name = ''.join([random.choice(characters) for _ in range(8)])

        match upload_type:
            case 'img':
                print('Uploading...')
                file_name = self.upload_image(b2_file_name)
            
            case upload_type if upload_type in self.b2_keys['txtTypes']:
                print('Local file?')
                local_file = input('>>> ')
                
                print('Uploading...')
                file_name = self.upload_text(b2_file_name, upload_type, local_file)
                
            case _:
                file_name = None

        if not file_name:
            return
        
        copy(export_url := f'https://{self.b2_keys["subDomain"]}/{file_name}')
        print(export_url)