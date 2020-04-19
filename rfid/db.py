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
    try:
        db = getConnection()
        cursor = db.cursor()

        checkQuery = "select * from cards where uid=%s"
        cursor.execute(checkQuery, uid)
        check = cursor.fetchall()
        if len(check) > 0:
            cursor.close()
            db.close()
            return False
        cardSql = "insert into cards (uid,status) values (%s, %s)"
        cursor.execute(cardSql, (uid, 100))
        insertId = cursor.lastrowid
        userSql = "insert into users (card_id,name,surname) values (%s,%s,%s)"
        cursor.execute(userSql, (insertId, name, surname))

        db.commit()
        cursor.close()
        db.close()
        return True
    except:
        return False


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
