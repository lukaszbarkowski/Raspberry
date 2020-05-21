from flask import Flask, request, Response, copy_current_request_context, jsonify
import json
import time
import RPi.GPIO as GPIO
from pirc522 import RFID
import _thread
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from db import addNewUser, getAllUsers, removeUserById

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

rdr = RFID()
util = rdr.util()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode="threading", path='/ws',
                    logging=True, engineio_logger=True, cors_allowed_origins='*')

readMode = "default"


def switchMode(mode):
    global readMode
    if mode == "newUser":
        GPIO.output(8, GPIO.HIGH)
    elif mode == "default":
        GPIO.output(8, GPIO.LOW)
    readMode = mode


@app.route("/remove_user/<id>", methods=['DELETE'])
def remove_user(user_id):
    if request.method == 'DELETE':
        isUserRemoved = removeUserById(user_id)
        if isUserRemoved:
            return Response(mimetype="application/json", status=204)
        else:
            return Response(mimetype="application/json", status=400)



@app.route("/add_user", methods=['POST'])
def add_user():
    if request.method == 'POST':
        req=request.get_json()
        userAdded=addNewUser(req['uid'], req['name'], req['surname'])
        if userAdded:
            return Response(mimetype="application/json", status=201)
        else:
            return Response(mimetype="application/json", status=400)


@app.route("/all_users")
def get_users():
    users=getAllUsers()
    return jsonify(users)


@socketio.on("connect")
def onConnect():
    switchMode("newUser")


@socketio.on("disconnect")
def onConnect():
    switchMode("default")


def emitFromBackground(uid):
    socketio.emit('set_uuid', {"data": uid})


def read():
    while True:
        global readMode
        if readMode == "newUser":
            rdr.wait_for_tag()
            (error, tag_type)=rdr.request()
            if not error:
                (error, uid)=rdr.anticoll()
                emitFromBackground(uid)
    rdr.cleanup()


if __name__ == "__main__":

    _thread.start_new_thread(read, ())
    socketio.run(app, host="0.0.0.0", log_output=True)
