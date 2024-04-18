import json
import urllib.request
from urllib.parse import quote

from flask import redirect, render_template, request


def request_url(url: str):
    req = urllib.request.Request(url, method='GET')

    with urllib.request.urlopen(req) as response:
        data = response.read()

    return json.loads(data)

def get_url(claim_data: dict, ids: str):
    if not (claim_ids := claim_data.get(ids, None)):
        return
    
    return claim_ids[0]['mainsnak']['datavalue']['value']
 
def wiki_search():
    query = initial_query = request.args.get('q', default='', type=str)
    
    if not initial_query:
        return render_template('index.html')
    
    lang = 'en'
    if '.' in initial_query:
        lang = (query_split := initial_query.split('.'))[-1]
        query = '.'.join(query_split[:-1])

    result_query = request_url(f'https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language={lang}&limit=1&search={quote(query)}')
    
    # with open('data.json', 'w', encoding='utf-8') as fw:
    #     json.dump(result_query, fw, ensure_ascii=False, indent=2)

    if not result_query['search']:
        return redirect(f'https://www.startpage.com/sp/search?query={query}&cat=web&pl=opensearch&language=english')

    item_id = result_query['search'][0]['id']

    result_id = request_url(f'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={item_id}&props=claims')
    claim_data = result_id['entities'][item_id]['claims']

    for ids in ['P856', 'P1324']:
        if not (url := get_url(claim_data, ids)):
            continue

        return redirect(url)

    return redirect(f'https://www.startpage.com/sp/search?query={query}&cat=web&pl=opensearch&language=english')