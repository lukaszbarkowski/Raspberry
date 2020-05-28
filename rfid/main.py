from flask import Flask, request, Response, copy_current_request_context, jsonify
import json
import time
import RPi.GPIO as GPIO
from pirc522 import RFID
import _thread
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from db import addNewUser, getAllUsers, removeUserById, checkCard
from threading import Timer

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(36, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(38, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(40, GPIO.OUT, initial=GPIO.LOW)

rdr = RFID()
util = rdr.util()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode="threading", path='/ws',
                    logging=True, engineio_logger=True, cors_allowed_origins='*')

readMode = "default"
newUser = False
wait = False

def switchMode(mode):
    global readMode
    if mode == "access_granted":
        GPIO.output(36, GPIO.LOW)
        GPIO.output(38, GPIO.HIGH)
        GPIO.output(40, GPIO.LOW)
    elif mode == "access_denied":
        GPIO.output(38, GPIO.LOW)
        GPIO.output(36, GPIO.HIGH)
        GPIO.output(40, GPIO.LOW)
    elif mode == "default":
        GPIO.output(36, GPIO.HIGH)
        GPIO.output(38, GPIO.HIGH)
        GPIO.output(40, GPIO.LOW)
    readMode = mode

def toggleAccessCheck():
    global wait
    GPIO.output(36, GPIO.HIGH)
    GPIO.output(38, GPIO.HIGH)
    GPIO.output(40, GPIO.LOW)
    wait = False
    


@app.route("/remove_user/<id>", methods=['DELETE'])
def remove_user(id):
    if request.method == 'DELETE':
        isUserRemoved = removeUserById(id)
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
    global newUser
    newUser = True
    GPIO.output(32, GPIO.HIGH)

@socketio.on("disconnect")
def onConnect():
    global newUser
    newUser = False
    GPIO.output(32, GPIO.LOW)

def emitFromBackground(uid):
    socketio.emit('set_uuid', {"data": uid})

def read():
    while True:
        global readMode
        global wait
        rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        if not error:
            (error, uid) = rdr.anticoll()
            if newUser:
                emitFromBackground(uid)
            if not wait:
                isAccessGranted = checkCard(uid)
                if isAccessGranted:
                    switchMode("access_granted")
                    t = Timer(3.0,toggleAccessCheck)
                    t.start()
                else:
                    switchMode("access_denied")
                    t = Timer(3.0, toggleAccessCheck)
                    t.start()
    rdr.cleanup()


if __name__ == "__main__":

    _thread.start_new_thread(read, ())
    socketio.run(app, host="0.0.0.0", log_output=True)
    GPIO.cleanup()
