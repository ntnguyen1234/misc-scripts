import json

from backblaze import B2


def main():
    orig_file = input('\nUpload file from?\n1. Clipboard\n2. Local path\n>>> ')
    if orig_file not in ("1", "2"):
        exit()

    with open('b2.json', 'r', encoding='utf-8') as fr:
        b2_keys = json.load(fr)

    (upload_types := b2_keys['uploadTypes']).extend(b2_keys['txtTypes'])
    
    upload_type = input(f'\nUpload type? ({", ".join(upload_types)})\n>>> ')
    if upload_type not in upload_types:
        exit()

    b2_app = B2(b2_keys)
    
    print('\nAuthorizing...')
    b2_app.authorize()

    b2_app.upload_general(orig_file, upload_type)

    input('')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()