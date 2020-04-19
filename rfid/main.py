from flask import Flask, request, Response, copy_current_request_context, jsonify
import json
import time
import RPi.GPIO as GPIO
from pirc522 import RFID
import _thread
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from db import addNewUser, getAllUsers

GPIO.setmode(GPIO.BOARD)

rdr = RFID()
util = rdr.util()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode="threading", path='/ws',
                    logging=True, engineio_logger=True, cors_allowed_origins='*')


@app.route("/hello")
def hello():
    return Response('{"someData":"Hello World!"}', mimetype="application/json", status=200)


@app.route("/add_user", methods=['POST'])
def add_user():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        addNewUser(req['uid'], req['name'], req['surname'])
        return Response(mimetype="application/json", status=200)


@app.route("/get_users")
def get_users():
    users = getAllUsers()
    return jsonify(users)


@socketio.on("connect")
def testConnection():
    print("Got something!")


# set to true when sensor detects card
# set to false when saving user
isTagSet = False


def emitFromBackground(uid):
    socketio.emit('set_uuid', {"data": uid})


def read():
    while True:
        global isTagSet
        if not isTagSet:
            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                (error, uid) = rdr.anticoll()
                isTagSet = True
                emitFromBackground(uid)
    rdr.cleanup()


if __name__ == "__main__":

    _thread.start_new_thread(read, ())
    socketio.run(app, host="0.0.0.0", log_output=True)
