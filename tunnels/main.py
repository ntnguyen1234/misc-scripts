import json
import ssl
from multiprocessing import Process

import httpx
from icecream import ic
from tunnels_all import Tunnels


def main():
    with open('config.json', 'r', encoding='utf-8') as fr:
        configs = json.load(fr)

    # tunnel_apps = Tunnels(configs)
    # functions = [
    #     tunnel_apps.psitransfer,
    #     tunnel_apps.cf_tunnel,
    #     tunnel_apps.push_to_pastefy
    # ]

    # try:
    #     processes: list[Process] = []
    #     for f in functions:
    #         proc = Process(target=f)
    #         proc.start()
    #         processes.append(proc)

    #     for proc in processes:
    #         proc.join()
        
    #     tunnel_apps.cleanup()
        
    # except KeyboardInterrupt:
    #     tunnel_apps.cleanup()
        
    idx = configs['ltn_idx']
    local_token = configs['ltn_token']
    with httpx.Client(verify=ssl.create_default_context()) as client:
        # url = f'https://localtonet.com/api/StartTunnel/:{idx}'
        url = 'https://localtonet.com/api/GetTunnels'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {local_token}'
        }

        response = client.get(url, headers=headers)
        ic(response.json())


if __name__ == "__main__":
    main()
