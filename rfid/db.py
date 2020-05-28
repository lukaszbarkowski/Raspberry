import mysql.connector


def getConnection():
    db = mysql.connector.connect(
        host="localhost",
        user="admin",
        passwd="qwerty123",
        database="rfid"
    )
    return db


def addNewUser(uid, name, surname):
    db = getConnection()
    cursor = db.cursor()
    checkQuery = "select card from users where card=" + str(uid)
    cursor.execute(checkQuery)
    check = cursor.fetchall()
    print(check)
    if len(check) > 0:
        cursor.close()
        db.close()
        return False
    userSql = "insert into users (card,name,surname) values (%s,%s,%s)"
    cursor.execute(userSql, (uid, name, surname))
    db.commit()
    cursor.close()
    db.close()
    return True

def checkCard(uid):
    db = getConnection()
    cursor = db.cursor()
    card_id = ''
    for i in uid:
        card_id = card_id + str(i)
    checkQuery = "select * from users where card=" + card_id
    cursor.execute(checkQuery)
    check = cursor.fetchall()
    cursor.close()
    db.close()
    if len(check)>0:
        return True
    return False

def removeUserById(id):
    db = getConnection()
    cursor = db.cursor()
    removeQuery = "delete from users where id =" + str(id)
    cursor.execute(removeQuery)
    db.commit()
    cursor.close()
    db.close()
    return True

def getAllUsers():
    db = getConnection()
    cursor = db.cursor()
    sql = "select * from users"
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()

    return result
