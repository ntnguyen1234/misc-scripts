import search
import wiki
from flask import Flask

app = Flask(__name__)

app.add_url_rule('/wiki', view_func=wiki.wiki_search)
app.add_url_rule('/search', view_func=search.kagi_search)
    
 
if __name__ == "__main__":
    app.run(port=8200)