import re

from icecream import ic
from ubo_utils import load_json


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
            if key in ['uBlock Origin', 'browser']:
                continue

            if f'{key}: ' not in self.text:
                continue

            self.troubleshoot[key] = template[key]

    def extract_value(self, key: str, pattern: str) -> str:
        extract = re.search(pattern, self.text)[0].strip()
        return extract.split(f'{key}:')[-1].strip()

    def summary(self, key: str):
        value = self.extract_value(key, r'filterset.+?(?=listset)')

        for filter_type, num in re.findall(r'(\w+): (\d+)', value):
            self.troubleshoot[key][filter_type] = int(num)

    def listset(self, key: str):
        value = self.extract_value(key, r'listset.+?(?=filterset)')

        ls_dict = dict()
        pattern = r''
        for k in self.troubleshoot[key]:
            if f'{k}: ' not in value:
                continue

            ls_dict[k] = dict()
            pattern = rf'{pattern}{k}:(.*)'

        for k, extract in zip(ls_dict.keys(), re.findall(pattern, value)[0]):
            extract: str
            for link, stats in re.findall(r'(\S+) (\d+\-\d+, [.\w]+)', extract.strip()):
                ls_dict[k][link] = stats

        self.troubleshoot[key] = ls_dict

    def others(self, key: str):
        if '(user)' in key:
            value = self.extract_value(key, r'filterset \(user\):.+?(?=(?:[a-zA-Z]+: ){2})')
        else:
            value = self.extract_value(key, rf'{key}:.+?(?=(?:[a-zA-Z]+: ){{2}})')
        
        if ':' not in value:
            self.troubleshoot[key] = value
        else:
            self.troubleshoot[key] = dict()
            for k, extract in re.findall(r'(\w+): (.+?(?=(?: \w+:|$)))', value):
                extract: str
                self.troubleshoot[key][k] = int(extract) if extract.isnumeric() else extract