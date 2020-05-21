import mysql.connector;

db = mysql.connector.connect(host="localhost",user="admin",passwd="qwerty123")

cursor = db.cursor()

#cursor.execute("create database if not exists rfid")

cursor.execute("use rfid")

cursor.execute('''
    create table if not exists users(
        id INT AUTO_INCREMENT,
        card INT,
        name varchar(32),
        surname varchar(64),
        primary key(id),
    )    
''')

