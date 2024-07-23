import io
import secrets
import string
from pathlib import Path

from b2sdk import v2 as b2
from PIL import ImageGrab
from pyclip import copy, paste


def random_name() -> str:
    init_name = input('\nInit name\n>>> ')
    alphabet = string.ascii_letters + string.digits
    return init_name + '-' + ''.join(secrets.choice(alphabet) for i in range(8))

class B2:
    def __init__(self, b2_keys: dict[str, str]):
        self.info = b2.InMemoryAccountInfo()
        self.b2_api = b2.B2Api(self.info, cache=b2.AuthInfoCache(self.info))

        self.b2_keys = b2_keys
    
    def authorize(self):
        self.b2_api.authorize_account('production', self.b2_keys['keyID'], self.b2_keys['applicationKey'])
        self.bucket = self.b2_api.get_bucket_by_name(self.b2_keys['bucketName'])

    def upload_image(self, b2_file_name: str) -> str:
        if isinstance((img := ImageGrab.grabclipboard()), list):
            file_name = ""
        else:
            if (img_format := img.format).lower() not in self.b2_keys['imgTypes']:
                print('\nNot images\n')
                exit()
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=img_format)
            img_bytes = img_bytes.getvalue()

            response = self.bucket.upload_bytes(
                data_bytes=img_bytes,
                file_name=(file_name := f'img/{b2_file_name}.{img_format.lower()}')
            )
            print('')
            print(response, end='\n\n')

        return file_name
    
    def upload_file(self, b2_file_name: str, upload_type: str, local_file: Path) -> str:
        if upload_type == 'media':
            suffix = local_file.suffix.lower().strip('.')
        else:
            suffix = upload_type.lower()

        file_name = f'{upload_type}/{b2_file_name}.{suffix}'
        
        self.bucket.upload_local_file(
            local_file=local_file,
            file_name=file_name
        )
            
        return file_name
    
    def upload_from_clipboard(self, upload_type: str, b2_file_name: str):
        if upload_type == 'img':
            self.upload_image(b2_file_name)

    def upload_general(self, orig_file: str, upload_type: str):
        uploaded_name = ''

        if orig_file == "1": # Clipboard
            b2_file_name = random_name()
            if upload_type != 'img':
                print('\nClipboard only supports images\n')
                exit()
            uploaded_name = self.upload_image(b2_file_name)
        else:  # Local file
            local_file = Path(input('\nCopy local file path to here\n>>> ').strip('"')).absolute()
            if not local_file.is_file():
                print(f'\nNo file at {str(local_file)}\n')
                exit()

            rename_file = input('\nDo you want to rename file? (y/n)\n>>> ').lower()
            if rename_file in ('y', 'yes'):
                b2_file_name = random_name()
            elif rename_file in ('n', 'no'):
                b2_file_name = local_file.stem
            else:
                exit()

            uploaded_name = self.upload_file(b2_file_name, upload_type, local_file)

        if not uploaded_name:
            exit()
        
        copy(export_url := f'https://{self.b2_keys["subDomain"]}/{uploaded_name}')
        print('\n' + export_url)