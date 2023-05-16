import re

from icecream import ic
from ubo_utils import load_json


def get_search(pattern: str, text: str) -> dict[str, str]:
    return {k: v for k, v in re.findall(pattern, text)}


class Reformatter:
    __slots__ = ('text', 'troubleshoot')

    def __init__(self):
        self.troubleshoot = dict()

    def load_template(self, text: str):
        self.text = text

        patterns = [
            r'(uBlock Origin): (\d\.\d{2}\.\w+)',
            r'((?:Chromium|Firefox)(?: Mobile)?): (\d+)'
        ]
        for pattern in patterns:
            extract = re.search(pattern, self.text)
            self.troubleshoot[extract.group(1)] = extract.group(2)

        for key in (template := load_json('template.json')):
            if key in {'uBlock Origin', 'browser'}:
                continue

            if f'{key}: ' not in self.text:
                continue

            self.troubleshoot[key] = template[key]

    def extract_value(self, key: str, pattern: str, text: str = None) -> str:
        extract = re.search(pattern, text or self.text)[0].strip()
        return extract.split(f'{key}:')[-1].strip()

    def summary(self, key: str):
        value = self.extract_value(key, r'filterset.+?(?=listset)')
        self.troubleshoot[key] = get_search(r'(\w+): (\d+)', value)

    def listset(self, key: str):
        value = self.extract_value(key, r'listset.+?(?=filterset)')
        for k in ['removed', 'added', 'default']:
            if f'{k}: ' not in value:
                continue
            
            extract = self.extract_value(k, rf'{k}: (.+?(?=(?:(?:\S+: ){{2}})|$))', value)
            self.troubleshoot[key][k] = get_search(r'(\S+): (\d+\-\d+, [.\w]+)', extract.strip())

    def others(self, key: str):
        if 'popup' in key:
            value = self.extract_value(key, r'popupPanel.*')
        elif '(user)' in key:
            value = self.extract_value(key, r'filterset \(user\):.+?(?=(?:[a-zA-Z]+: ){2})')
        else:
            value = self.extract_value(key, rf'{key}:.+?(?=(?:[a-zA-Z]+: ){{2}})')
        
        if ':' not in value:
            self.troubleshoot[key] = value
            return
        
        for k, extract in re.findall(r'(\w+): (.+?(?=(?: \w+:|$)))', value):
            extract: str
            match k:
                case 'cosmetic':
                    self.troubleshoot[key][k] = [f'##{item}'.replace('####', '##') for item in extract.split(' ##')]
                case 'network':
                    self.troubleshoot[key][k] = get_search(r'([.\w]+): (.+?(?=(?: [.\w]+:|$)))', extract)
                case _:
                    self.troubleshoot[key][k] = int(extract) if extract.isnumeric() else extract