from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import Crypto_Stegano as cs
from PIL import Image
#qrcode
from pyzbar.pyzbar import decode
# hash
import secrets
import hashlib
import signature as si
#BDD
import initdb

class messSign:
    "def classe message signature"

def creationSignature2(nom, prenom, cert, timestamp):
    boolMeSi = messSign()
    message = nom + " " + prenom +" || " + cert + " ||"
    if len(message) <64:
        for i in range(64-len(message)):
            message = message+ " "
    message = message + " || " + timestamp + " ||++"
    infosHash = hashlib.sha256(message.encode()).hexdigest()
    boolMeSi.message = infosHash.encode()
    # décommenter si pas de clés
    # si.genKey()
    messageSigne = si.alice(infosHash)
    # On encode
    boolMeSi.signature = base64.b64encode(messageSigne)
    return boolMeSi

def bob(signature,infohash):

    signature = base64.b64decode(signature)
    key = RSA.importKey(open('public.pem').read())
    h = SHA.new()
    h.update(infohash)
    verifier = PKCS1_PSS.new(key)
    if verifier.verify(h, signature):
        print("La signature est authentique.")
    else:
        print("La signature n'est pas authentique.")
    return verifier.verify(h, signature)

def extrairePreuve(nom, prenom, diplome, nomImage):
    #Vérification timestamp
    conn,cursor= initdb.connectDB()
    initdb.initDB()
    cursor.execute("""SELECT dateDemande FROM demandesDiplome WHERE nom = %s AND prenom = %s AND diplome = %s""", (nom,prenom,diplome))
    row = cursor.fetchall()
    timestamp = row[0][0]
    #Vérification signature
    img = Image.open("../sources/"+nomImage)
    data = decode(img)
    signature = data[0][0]
    boolMeSi = messSign()
    boolMeSi = creationSignature2(nom, prenom, diplome, timestamp)
    print(signature)
    bob(signature,boolMeSi.message)
    conn.close()

