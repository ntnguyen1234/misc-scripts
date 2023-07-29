import json
from pathlib import PosixPath, WindowsPath


def load_json(file_path: str | PosixPath | WindowsPath) -> list | dict:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return json.load(fr)
    

def write_json(data, file_path: str | PosixPath | WindowsPath):
    with open(file_path, 'w', encoding='utf-8', errors='surrogateescape') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)