import mimetypes

import page_redirect
import search
import wiki
from flask import Flask

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__)

app.add_url_rule('/wiki', view_func=wiki.wiki_search)
app.add_url_rule('/search', view_func=search.kagi_search)
app.add_url_rule('/redirect', view_func=page_redirect.redirect_url)

 
if __name__ == "__main__":
    app.run(port=8200)