# Écrire sur l'image
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
# signature
from base64 import (
    b64encode,
    b64decode,
)
import base64

# Redimensionner l'image
import cv2
import numpy as np
# hash
import secrets
import hashlib
# qrcode
import qrcode
# database
import initdb
# import fichier
import signature as si
import verification as ve
import Crypto_Stegano as cs
# On ouvre la connection avec la base de données
conn, cursor = initdb.connectDB()

class Etudiant:
    "def classe etudiant"

class messSign:
    "def classe message signature"

def creationDiplome(nom, prenom, cert, idDemande,timestamp):
    nomFichier = "diplome"+nom+prenom+".png"
    # On ajoute les écritures
    W, H = (1750, 1240)
    im = Image.open("../docs/2021-2022-Projet_Crypto_Fond_Attestation.png")
    im = im.resize((W, H))
    font = ImageFont.truetype("../sources/font/times.ttf", 90)
    draw = ImageDraw.Draw(im)
    draw.text((450.0, 460.0), "CERTIFICAT DÉLIVRÉ", (1, 1, 1), font=font)
    w2, h2 = draw.textsize("À")
    draw.text(((-20+(W-w2)/2),-60+((H-h2)/2)), "À", (1, 1, 1), font=font)
    msg = prenom+" "+nom
    w1, h1 = draw.textsize(msg)
    draw.text((-250+((W-w1)/2),20+((H-h1)/2)), msg, (1, 1, 1), font=font)
    w,h = draw.textsize(cert)
    draw.text((-350+((W-w)/2),100+((H-h)/2)), cert, (1, 1, 1), font=font)

    im.save("../sources/"+nomFichier, "PNG")

    # On récupère la signature
    boolMeSi = messSign()
    boolMeSi = creationSignature(nom, prenom, cert, timestamp)
    # On ajoute le qr code
    qrcodeG(boolMeSi.signature)
    qr = Image.open("../sources/qr.png")
    qr = qr.resize((200, 200))
    # On place l'image (x,y)
    im.paste(qr, (1420, 930))
    # Redimensioner le qr code
    im.save("../sources/"+nomFichier, "PNG")
    #Dissimulation par stéganographie
    cs.cacherMain(nomFichier, idDemande)
    return nomFichier

def creationSignature(nom, prenom, cert, timestamp):
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

def qrcodeG(signature):
    img = qrcode.make(signature)
    type(img)
    # qrcodeDir.image.pil.PilImage
    img.save("../sources/qr.png")
    return 0
