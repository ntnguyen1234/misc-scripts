import json
import subprocess
import time
from pathlib import Path

from pastefy_web import Pastefy
from utils import load_text


class Tunnels:
    def __init__(self, configs: dict):
        self.configs = configs
        self.pastefy_app = Pastefy(self.configs)
        self.pastefy_json = {'direct': '', 'cloud': ''}

    @staticmethod
    def get_url():
        while not (cf_log := Path('cf_log.txt')).exists():
            time.sleep(1)
            continue

        url = ''
        while not url:
            for line in load_text(cf_log, True):
                msg: str = json.loads(line)['message']
                msg = msg.replace('|', '').strip()
                if not msg.endswith('trycloudflare.com'):
                    continue
                
                url = msg
                break

        return url
    
    def cleanup(self):
        for file_path in Path().rglob('*_log.txt'):
            file_path.unlink()

        self.pastefy_json['direct'] = ''
        self.pastefy_app.pastefy_edit(json.dumps(self.pastefy_json))


    def psitransfer(self):
        subprocess.run(
            ['npm.cmd', 'start'],
            cwd=self.configs['psi_dir'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def cf_tunnel(self):
        subprocess.run(
            [
                'cloudflared', 'tunnel', 
                '--logfile', 'cf_log.txt',
                '--url', f'http://localhost:{self.configs["port"]}'
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def push_to_pastefy(self):
        url = self.get_url()
        
        self.pastefy_json = self.pastefy_app.get_pastefy()
        self.pastefy_json['direct'] = url

        self.pastefy_app.pastefy_edit(json.dumps(self.pastefy_json))