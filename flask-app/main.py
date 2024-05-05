from base64 import b64decode, b64encode, urlsafe_b64decode, urlsafe_b64encode

import nacl.secret
import nacl.utils
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes


def main():
    key = bytes.fromhex('724b092810ec86d7e35c9d067702b31ef90bc43a7b598626749914d6a3e033ed')
    # nonce = urlsafe_b64decode('b0YonXz_l5puhJXZReQ5OHw2zAps1M43')
    # ciphertext = urlsafe_b64decode('qI32qCoxDkkeJH0AVYu4JxPOwOnx')
    
    nonce = bytes.fromhex('6f46289d7cff979a6e8495d945e439387c36cc0a6cd4ce37')
    ciphertext = bytes.fromhex('a88df6a82a310e491e247d00558bb82713cec0e9f1')

    # cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    # plaintext = cipher.decrypt(ciphertext)

    # print(nonce)
    # print(ciphertext)
    # print(plaintext)

    # plaintext = b'Attack at dawn'
    # key = get_random_bytes(32)
    # key = bytes.fromhex('724b092810ec86d7e35c9d067702b31ef90bc43a7b598626749914d6a3e033ed')
    # cipher = ChaCha20_Poly1305.new(key=key)
    # ciphertext = cipher.encrypt(plaintext)

    # print(ciphertext)

    # nonce = urlsafe_b64encode(cipher.nonce)
    # ct = urlsafe_b64encode(ciphertext)

    # print(key)
    # print(nonce, type(nonce))
    # print(ct, type(ct))

    # print(urlsafe_b64decode(nonce))
    # print(urlsafe_b64decode(ct))

    # cipher2 = ChaCha20_Poly1305.new(key=key, nonce=urlsafe_b64decode(nonce))
    # print(cipher2.decrypt(urlsafe_b64decode(ct)))

    box = nacl.secret.Aead(key)
    plain = box.decrypt(ciphertext=ciphertext, nonce=nonce)
    print(plain)


if __name__ == '__main__':
    main()