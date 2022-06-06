from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto import Random
import base64


def conversionAscii(signature):
    text = str(signature)
    ascii_values = []
    for character in text:
        ascii_values.append(ord(character))
    return ascii_values


def alice(message):
    message = message.encode()
    key = RSA.importKey(open('private.pem').read())
    h = SHA.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)
    signature = signer.sign(h)
    return signature





def genKey():
    keyprivate = RSA.generate(1024)
    k = keyprivate.exportKey('PEM')
    p = keyprivate.publickey().exportKey('PEM')
    with open('private.pem', 'w') as kf:
        kf.write(k.decode())
        kf.close()
    with open('public.pem', 'w') as pf:
        pf.write(p.decode())
        pf.close()
