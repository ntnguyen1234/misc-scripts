import json

from backblaze import B2


def main():
    print('Upload type?')
    if not (upload_type := input('>>> ')):
        return

    with open('b2.json', 'r', encoding='utf-8') as fr:
        b2_keys = json.load(fr)

    b2_app = B2(b2_keys)
    
    print('Authorizing...')
    b2_app.authorize()
    
    b2_app.upload_from_clipboard(upload_type)


if __name__ == "__main__":
    main()