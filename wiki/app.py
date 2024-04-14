import json
import urllib.request
from urllib.parse import quote

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

def request_url(url: str):
    req = urllib.request.Request(url, method='GET')

    with urllib.request.urlopen(req) as response:
        data = response.read()

    return json.loads(data)

def get_url(claim_data: dict, ids: str):
    if not (claim_ids := claim_data.get(ids, None)):
        return
    
    return claim_ids[0]['mainsnak']['datavalue']['value']
 
@app.route('/wiki')
def hello_world():
    query = quote(request.args.get('q', default='', type=str))
    
    if not query:
        return render_template('index.html')

    result_query = request_url(f'https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&limit=1&search={query}')
    item_id = result_query['search'][0]['id']
    print(item_id)

    result_id = request_url(f'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={item_id}&props=claims')
    claim_data = result_id['entities'][item_id]['claims']

    # with open('data.json', 'w', encoding='utf-8') as fw:
    #     json.dump(claim_data, fw, ensure_ascii=False, indent=2)

    for ids in ['P856', 'P1324']:
        if not (url := get_url(claim_data, ids)):
            continue

        return redirect(url)

    return redirect(f'https://www.startpage.com/sp/search?query={query}')
    
 
if __name__ == "__main__":
    app.run(port=8200)