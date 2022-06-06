import base64
import datetime
import hashlib
import secrets
import smtplib
import ssl
import subprocess
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pyotp

import Crypto_Stegano
import creerattestation as ca
import initdb
import verification

import qrcode


# On ouvre la connection avec la base de données
conn,cursor = initdb.connectDB()
# On initialise la DB
initdb.initDB()

def creerAdmin(login, password):
    rd = secrets.token_hex(8).upper()
    admin = {
        "login": login,
        "password": password,
        "rd": rd
    }
    cursor.execute("""
        INSERT INTO admins (
            login, 
            password,
            rd
        ) 
        VALUES (
            %(login)s, 
            %(password)s, 
            %(rd)s
        )""", admin)
    conn.commit()

def ajouterDemandeDiplome(nom, prenom, email, diplome):
    dateDemande = str(datetime.date.today())
    demande = {
        "nom": nom,
        "prenom": prenom,
        "email": email,
        "diplome": diplome,
        "dateDemande": dateDemande
    }
    cursor.execute("""
        INSERT INTO demandesDiplome (
            nom,
            prenom,
            email,
            diplome,
            dateDemande
        )
        VALUES (
            %(nom)s, 
            %(prenom)s, 
            %(email)s,
            %(diplome)s,
            %(dateDemande)s
        )
    """, demande)
    conn.commit()

def imageBase64(nomImage):
    image = open('../sources/'+nomImage, 'rb')
    data = base64.b64encode(image.read())
    image.close()
    contenu = open('../sources/contenu.txt', 'w')
    contenu.write("Content-Type: image/png\nContent-Transfer-Encoding: base64\n"+data.decode("utf-8"))
    contenu.close()

def commandeOpenSSL(nomImage, emailReceiver, emailSender):
    imageBase64(nomImage)
    result = subprocess.getoutput("cat ../sources/contenu.txt | openssl smime -signer public.pem -from "+emailSender+" -to "+emailReceiver+" -subject 'Envoi avec signature' -sign -inkey private.pem -out contenu_courrier.txt")
    print(result)
    return result

def envoyerMail(nom, prenom, emailReceiver, nomImage):
    # on rentre les renseignements pris sur le site du fournisseur
    smtp_address = 'smtp.gmail.com'
    smtp_port = 465

    # on rentre les informations sur notre adresse e-mail
    print("Veuillez fournir les informations de connexion de l'expéditeur : ")
    mail = str(input('Adresse mail :'))
    #mail = str('***')
    email_address = mail
    # Donner le mot de passe de l'app password de google
    password = str(input("Mot de passe de l'app password google : "))
    #password = str('***')
    email_password = password

    # on rentre les informations sur le destinataire
    email_receiver = emailReceiver

    # on crée un e-mail
    message = MIMEMultipart("alternative")
    # on ajoute un sujet
    message["Subject"] = "[CYTECH] Votre diplôme de fin d'année"
    # un émetteur
    message["From"] = email_address
    # un destinataire
    message["To"] = email_receiver

    html = '''
    <html>
        <body>
            <h1>Bonjour '''+nom+''' '''+prenom+'''</h1>
            <p>Veuillez trouver ci-joint votre diplôme.</p>
            <b>Cdt,</b>
            <br>
            <b>L'administration CYTECH</b>
            <br>
        </body>
    </html>
    '''

    # on crée l'élément MIMEText 
    html_mime = MIMEText(html, 'html')

    # on crée l'élément MIMEImage
    with open('../sources/'+nomImage, 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-Disposition', 'attachment', filename="../sources/"+nomImage)

    # on attache ces deux éléments
    message.attach(html_mime)

    # Envoi de courrier au format S/MIME, PKCS#7
    #texte_mime = MIMEText(commandeOpenSSL(nomImage,emailReceiver,email_address), 'plain')
    
    #message.attach(texte_mime)
    message.attach(img)

    # on crée la connexion
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
        # connexion au compte
        server.login(email_address, email_password)
        # envoi du mail
        server.sendmail(email_address, email_receiver, message.as_string())
        print("Mail envoyé.\n")

def consulterDemandes(login):
    print("\n\nVoici les demandes de diplômes qui sont en attentes :\n")
    cursor.execute("""SELECT * FROM demandesDiplome""")
    rows = cursor.fetchall()
    print("|            ID              |            Nom             |          Prénom            |           Email            |          Diplôme           |     Date de la demande     |")
    for row in rows:
        temp = '|'
        # print(row)
        for element in row:
            temp = temp + ' ' + str(element)
            for i in range(28-(len(str(element))+1)):
                temp = temp + ' '
            temp = temp + '|'
        print(temp)

    print("\nSélectionnez l'ID de la demande dont vous voulez extraire la preuve avant de la valider\n(ou 0 pour revenir en arrière) : ")
    choix = int(input('Choix : '))
    if choix == 0:
        return 0
    else: 
        cursor.execute("""SELECT * FROM demandesDiplome WHERE id = %s""", (choix, ))
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("\n\nErreur dans la saisie de l'ID...")
        else:
            print("\n\nVous avez selectionne :")
            print("Id : "+str(rows[0][0]))
            print("Nom : "+rows[0][1])
            print("Prénom : "+rows[0][2])
            print("Email : "+rows[0][3])
            print("Diplôme : "+rows[0][4])
            print("Date de la demande : "+rows[0][5])

            otp = input("\n\nPour valider la demande, veuillez saisir l'OTP généré par l'application adapté : ")
            cursor.execute("""SELECT password, rd FROM admins WHERE login = %s""", (login, ))
            row = cursor.fetchall()
            totp = pyotp.TOTP(base64.b32encode(hashlib.sha256((row[0][0]+row[0][1]).encode()).hexdigest().encode()))
            if totp.verify(otp):
                print("Identification réussie, la demande de diplôme a été approuvée et le document sera bientôt envoyé par mail à l'étudiant")
                # A FAIRE : GENERER LE DOCUMENTS ET L'ENVOYER PAR MAIL
                nomImage = ca.creationDiplome(rows[0][1],rows[0][2],rows[0][4],rows[0][0],rows[0][5])

                envoyerMail(rows[0][1],rows[0][2],rows[0][3],nomImage)
            else:
                print("Erreur dans la saisie de l'OTP")


def extraireInfos():
    print("\n\nVeuillez tout d'abord vous assurer que vous avez bien le diplôme dont vous voulez extraire les\ninformations dans le dossier sources")
    nomImage = str(input("Veuillez maintenant saisir le nom de l'image (exemple : diplome.png) : "))
    print("Veuillez saisir les informations présentes sur le diplôme\n")
    nom = str(input("Nom --> "))
    prenom = str(input("Prénom --> "))
    diplome = str(input("Diplôme --> "))
    print("\n\nVoici les informations dissimulées par stéganographie dans l'image :\n")
    print(Crypto_Stegano.retrouverMain(nomImage))
    print("\n\nVoici les informations dissimulées et signées dans le QRCode :\n")
    verification.extrairePreuve(nom, prenom, diplome, nomImage)

def admin():
    login = str(input('\n\nVeuillez saisir votre identifiant -->  '))
    password = str(input('Veuillez saisir votre mot de passe -->  '))

    connected = False
    alreadyExist = False

    cursor.execute("""SELECT id, login, password FROM admins WHERE login = %s""", (login, ))
    rows = cursor.fetchall()

    while not connected:
        # Si le tableau de retour est vide, alors l'identifiant n'existe pas encore ou l'utilisateur s'est trompé dans sa saisie
        if len(rows) == 0:
            print('\n\nErreur dans la saisie de votre identifiant ou de votre mot de passe. Voulez vous réessayer ou vous enregistrer ?')
            print('1- S\'enregistrer')
            print('2- Réessayer')
            choix = int(input('Choix : '))
            if choix != 1 and choix != 2:
                print('\n\n/!\ Veuillez saisir un choix valide /!\\')
            if choix == 1:
                login_temp = str(input('\n\nVeuillez saisir votre identifiant -->  '))
                cursor.execute("""SELECT id, login FROM admins""")
                rows = cursor.fetchall()
                for row in rows:
                    if login == row[1]:
                        print('\n\n/!\ Il existe déjà un admin avec cet identifiant /!\\')
                        rows = []
                        alreadyExist = True
                if  not alreadyExist:
                    password_temp = input('Veuillez saisir votre mot de passe -->  ')
                    password_temp_conf = input('Veuillez confirmer votre mot de passe -->  ')
                    if hashlib.sha256(password_temp.encode()).hexdigest() != hashlib.sha256(password_temp_conf.encode()).hexdigest():
                        erreur_password = True
                    else:
                        erreur_password = False
                    while erreur_password:
                        print("\n\n/!\ Vos mots de passes ne correspondent pas /!\\\n\n")
                        password_temp = input('Veuillez saisir votre mot de passe -->  ')
                        password_temp_conf = input('Veuillez confirmer votre mot de passe -->  ')
                        if hashlib.sha256(password_temp.encode()).hexdigest() == hashlib.sha256(password_temp_conf.encode()).hexdigest():
                            erreur_password = False
                    creerAdmin(login_temp, hashlib.sha256(password_temp.encode()).hexdigest())
                    cursor.execute("""SELECT id, login, password FROM admins WHERE login = %s""", (login_temp, ))
                    login = login_temp
                    password = password_temp
                    rows = cursor.fetchall()
                    connected = True
            if choix == 2:
                login = str(input('\n\nVeuillez saisir votre identifiant -->  '))
                password = str(input('Veuillez saisir votre mot de passe -->  '))
                cursor.execute("""SELECT id, login, password FROM admins WHERE login = %s""", (login, ))
                rows = cursor.fetchall()
                connected = False

        if len(rows) > 0:
            for row in rows:
                if login == row[1] and hashlib.sha256(password.encode()).hexdigest() == row[2]:
                    connected = True
                    print("\n\nVous êtes bien connecté !")
                else:
                    connected = False
                    rows = []

    while connected:
        print("\n\nVoulez vous :\n1) Déposer une demande de diplôme\n2) Valider des demandes de diplômes\n3) Déconnexion")
        choix = int(input('Choix : '))
        if choix != 1 and choix != 2 and choix != 3:
            print('\n\n/!\ Veuillez saisir un choix valide /!\\')
        if choix == 1:
            demandeDiplome()
        if choix == 2:
            consulterDemandes(login)
        if choix == 3:
            connected = False

def demandeDiplome():
    print("\n\nVeuillez saisir les informations nécessaire au dépôt de la demande de diplôme\n")
    nom = str(input("Saisir le nom de l'étudiant --> ")).upper()
    prenom = str(input("Saisir le prénom de l'étudiant --> "))
    email = str(input("Saisir le mail de l'étudiant (il sera utilisé pour lui envoyé son diplôme une fois validé) --> "))
    diplome = str(input("Saisir le diplôme de l'étudiant, il figurera sur son diplôme (Ingénieur en cybersécurité, Ingénieur en IA, ...) --> "))
    ajouterDemandeDiplome(nom, prenom, email, diplome)



def main():
    quitterApplication = False
    while not quitterApplication:
        print("\n\nVoulez vous :\n1) Vous identifier en tant qu'administrateur\n2) Déposer une demande de diplôme\n3) Extraire les informations d'une image\n4) Quitter l'application")
        choix = int(input('Choix : '))
        if choix != 1 and choix != 2 and choix != 3 and choix != 4:
            print('\n\n/!\ Veuillez saisir un choix valide /!\\')
        if choix == 1:
            admin()
        if choix == 2:
            demandeDiplome()
        if choix == 3:
            extraireInfos()
        if choix == 4:
            quitterApplication = True

main()

# On ferme la connection
conn.close()
