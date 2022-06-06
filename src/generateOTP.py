import pyotp, time
import mysql.connector
import initdb
import hashlib
import base64

# On ouvre la connection avec la base de données
conn,cursor = initdb.connectDB()

#Identification de l'utilisateur 
login = str(input('Veuillez saisir votre identifiant -->  '))
password = str(input('Veuillez saisir votre mot de passe -->  '))

connected = False
disconnected = False

# On regarde si les informations saisies par l'utilisateur existe dans la bdd
cursor.execute("""SELECT id, login, password FROM admins WHERE login = %s""", (login, ))
rows = cursor.fetchall()

# On attend que l'utilisateur se connecte
while not connected and not disconnected:
    # Si le tableau de retour est vide, alors l'identifiant n'existe pas encore ou l'utilisateur s'est trompé dans sa saisie
    if len(rows) == 0:
        print("\n\nErreur dans la saisie de votre identifiant ou de votre mot de passe. Veuillez réessayer où allez vous créer un compe sur l'application principal.")
        print("Voulez vous réessayer où fermer l'application ?")
        print('1) Réessayer')
        print("2) Fermer l'application")
        choix = int(input('Choix : '))
        if choix != 1 and choix != 2:
            print('\n\n/!\ Veuillez saisir un choix valide /!\\')
        if choix == 1:
            login = str(input('\n\nVeuillez saisir votre identifiant -->  '))
            password = str(input('Veuillez saisir votre mot de passe -->  '))
            cursor.execute("""SELECT id, login, password FROM admins WHERE login = %s""", (login, ))
            rows = cursor.fetchall()
            connected = False
        if choix == 2:
            disconnected = True
        

    if len(rows) > 0:
        for row in rows:
            if login == row[1] and hashlib.sha256(password.encode()).hexdigest() == row[2]:
                connected = True
                print("\n\nVous êtes bien connecté !")
            else:
                connected = False
                rows = []

# l'utilisateur est maintenant connecté
while connected and not disconnected:
    print('Que voulez vous faire ?')
    print('1) Générer un OTP')
    print('2) Déconnexion')
    choix = int(input('Choix : '))
    # mauvaise saisie de l'utilisateur
    if choix != 1 and choix != 2:
        print('\n\n/!\ Veuillez saisir un choix valide /!\\')
    # l'utilisateur souhaite generer un OTP
    if choix == 1:
        cursor.execute("""SELECT password, rd FROM admins WHERE login = %s""", (login, ))
        row = cursor.fetchall()
        # on génère un otp valable pendant 30 sec
        totp = pyotp.TOTP(base64.b32encode(hashlib.sha256((row[0][0]+row[0][1]).encode()).hexdigest().encode()))
        print("\n\nVoici votre OTP, il est valable pendant 30 secondes : ",totp.now())
        print("\n\n")
    # l'utilisateur souhaite se déconnecter       
    if choix == 2:
        disconnected = True
conn.close()