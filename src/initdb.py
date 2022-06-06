import mysql.connector



def connectDB():
    conn = mysql.connector.connect(host='localhost', user='admin', password='admin', database='cryptoProjet')
    cursor = conn.cursor()
    return (conn,cursor)

def initDB():
    conn,cursor = connectDB()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id int(5) NOT NULL AUTO_INCREMENT,
            login VARCHAR(50) NOT NULL,
            password VARCHAR(64) NOT NULL,
            rd VARCHAR(50) NOT NULL,
            PRIMARY KEY(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demandesDiplome (
            id int(5) NOT NULL AUTO_INCREMENT,
            nom VARCHAR(50) NOT NULL,
            prenom VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL,
            diplome VARCHAR(50) NOT NULL,
            dateDemande VARCHAR(50) NOT NULL,
            PRIMARY KEY(id)
        )
    """)