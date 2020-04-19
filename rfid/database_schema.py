import mysql.connector;

db = mysql.connector.connect(host="localhost",user="admin",passwd="qwerty123")

cursor = db.cursor()

cursor.execute("create database if not exists rfid")

cursor.execute("use rfid")

cursor.execute('''
    create table if not exists cards(
        id int auto_increment,
        uid varchar(64),
        status boolean,
        primary key(id)
    )        
''')

cursor.execute('''
    create table if not exists users(
        id INT AUTO_INCREMENT,
        card_id int,
        name varchar(32),
        surname varchar(64),
        primary key(id),
        foreign key (card_id) references cards(id)
    )    
''')

cursor.execute('''
    create table if not exists access_history(
        card_id int,
        date datetime,
        foreign key (card_id) references cards(id)
    )        
''')


