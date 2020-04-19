import RPi.GPIO as GPIO
from pirc522 import RFID

GPIO.setmode(GPIO.BOARD)

rdr = RFID()
util = rdr.util()
util.debug = True
print("Start")
while True:
    print("wait")
    rdr.wait_for_tag()
    (error, tag_type) = rdr.request()
    if not error:
        (error, uid) = rdr.anticoll()
        print(uid)

# Calls GPIO cleanup
rdr.cleanup()
