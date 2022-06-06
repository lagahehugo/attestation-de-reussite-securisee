import initdb
from PIL import Image
import datetime

def vers_8bit(c):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	chaine_binaire = bin(ord(c))[2:]
	conn.close()
	return "0"*(8-len(chaine_binaire))+chaine_binaire

def modifier_pixel(pixel, bit):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	# on modifie que la composante rouge
	r_val = pixel[0]
	rep_binaire = bin(r_val)[2:]
	rep_bin_mod = rep_binaire[:-1] + bit
	r_val = int(rep_bin_mod, 2)
	conn.close()
	return tuple([r_val] + list(pixel[1:]))

def recuperer_bit_pfaible(pixel):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	r_val = pixel[0]
	conn.close()
	return bin(r_val)[-1]

def cacher(image,message):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	dimX,dimY = image.size
	im = image.load()
	message_binaire = ''.join([vers_8bit(c) for c in message])
	posx_pixel = 0
	posy_pixel = 0
	for bit in message_binaire:
		im[posx_pixel,posy_pixel] = modifier_pixel(im[posx_pixel,posy_pixel],bit)
		posx_pixel += 1
		if (posx_pixel == dimX):
			posx_pixel = 0
			posy_pixel += 1
		assert(posy_pixel < dimY)
	conn.close()

def recuperer(image,taille):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	message = ""
	dimX,dimY = image.size
	im = image.load()
	posx_pixel = 0
	posy_pixel = 0
	for rang_car in range(0,taille):
		rep_binaire = ""
		for rang_bit in range(0,8):
			rep_binaire += recuperer_bit_pfaible(im[posx_pixel,posy_pixel])
			posx_pixel +=1
			if (posx_pixel == dimX):
				posx_pixel = 0
				posy_pixel += 1
		message += chr(int(rep_binaire, 2))
	conn.close()
	return message

def cacherMain(nom, idDemande):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	nom_fichier = "../sources/"+nom

	cursor.execute("""SELECT nom, prenom, diplome, dateDemande FROM demandesDiplome WHERE id = %s""", (idDemande, ))
	row = cursor.fetchall()

	dateDemande= row[0][3].split('-')
	datetime_object = datetime.datetime(int(dateDemande[0]), int(dateDemande[1]), int(dateDemande[2]))
	seconds_since_epoch = datetime_object.timestamp()

	message_a_traiter = str(row[0][0])+" "+str(row[0][1])+" || "+str(row[0][2])+" ||"
	
	if len(message_a_traiter) < 64:
		for i in range(64 - len(message_a_traiter)):
			message_a_traiter = message_a_traiter+" "
	message_a_traiter = message_a_traiter +" || "+str(seconds_since_epoch).split(".")[0]+" ||"

	mon_image = Image.open(nom_fichier)
	cacher(mon_image, message_a_traiter)
	mon_image.save(nom_fichier)
	conn.close()
	return message_a_traiter

def retrouverMain(nom):
	# On ouvre la connection avec la base de données
	conn,cursor = initdb.connectDB()
	nom_fichier = "../sources/"+nom
	mon_image = Image.open(nom_fichier)
	# fixe a 81 car 64 pour les informations de l'etudiant et le reste pour le timestamp
	message_retrouve = recuperer(mon_image, 81)
	conn.close()
	return message_retrouve

