import nacl.secret
import nacl.utils
from flask import render_template, request
from twitter import get_tweet

from utils import load_text, write_text


def override_key():
    for _ in range(8):
        key_hex = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE).hex()
        write_text(key_hex, 'key.txt')


def redirect_url():
    key_hex = load_text('key.txt')
    print(key_hex)
    
    if not (query := request.args.get('token', default='', type=str)):
        return render_template('redirect_page.html', key_hex=key_hex)
    
    print(query.split('$')[1])

    key = bytes.fromhex(key_hex)
    nonce = bytes.fromhex(query.split('$')[0])
    ciphertext = bytes.fromhex(query.split('$')[1])

    aead = nacl.secret.Aead(key)
    url = aead.decrypt(ciphertext, nonce=nonce).decode(encoding='utf-8')

    override_key()
    get_tweet(url)
    # return redirect(url)
    return render_template('redirect_page.html', key_hex='')