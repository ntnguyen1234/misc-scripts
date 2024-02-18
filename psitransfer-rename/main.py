import json
from pathlib import Path


def load_json(file_path) -> list | dict:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return json.load(fr)


def main():
    data = Path(load_json('config.json')['data'])
    raw_files = [*data.rglob('*.json')]

    for file_path in raw_files:
        raw_file = file_path.parent / file_path.stem
        raw_name = load_json(file_path)['metadata']['name']

        print(raw_file, raw_name)

        raw_file.replace(file_path.parent / raw_name)


if __name__ == "__main__":
    main()
