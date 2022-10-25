import RPi.GPIO as GPIO  
from time import sleep 
 
receiverPin = 15
transmitterPin = 14
 
def handle_touch():
    if GPIO.event_detected(transmitterPin):
        print('touch sensor was pressed')
    else:
        print('touch sensor was not pressed')
    sleep(0.25)
 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #set up BCM GPIO numbering  
GPIO.setup(transmitterPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.add_event_detect(transmitterPin, GPIO.BOTH, callback=handle_touch)
msg = input("press something to exit program\n")
GPIO.cleanup()
