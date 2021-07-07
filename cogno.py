from Recognition import FacialIdentifier, AudioBuffer
from multiprocessing import Process, Pipe
from playsound import playsound
import RPi.GPIO as GPIO
import logging
import time
import uuid
import cv2
import os

class MainProcess():
    def __init__(self,display = False, facebase_path = "./Data/facebase", audiobase_path ="./Data/audiobase"):
        self.Face = FacialIdentifier(dbpath=facebase_path)
        self.AudioProcess = AudioBuffer(dbpath=audiobase_path)
        self.display = display
        self.f_path = facebase_path
        self.a_path = audiobase_path
        self.vid = cv2.VideoCapture(0)

    def identify(self):

        ret, frame = self.vid.read()
        if self.display == True:
            cv2.imshow('frame', frame)
        try:
            id = self.Face.get_person(frame,prob_threshold=1)
            print(id)
        except:
            print("No Face in Frame")
            return -1

        if id == -1:
            return False

        sounds = os.listdir(os.path.join(self.a_path,str(id)))
        playsound(os.path.join(os.path.join(self.a_path,str(id)),sounds[0]))
        return True

    def add_person(self,name = str(uuid.uuid4())):
        self.AudioProcess.save(name)
        ret, frame = self.vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.Face.add_face(frame,name)
        self.Face = FacialIdentifier(dbpath=self.f_path)

# Global variables used specifically for GPIO callback
GPIO_action = None
last_press = 0

def GPIO_callback(channel):
    global action, last_press

    press_time = round(time.time() * 1000)
    press_diff = press_time - last_press

    last_press = press_time
    action = 'double' if press_diff < 250 else 'single'

if __name__ == '__main__':
    M = MainProcess(display=False)
    # Set GPIO mode to BCM (not sure what it means but it works)
    GPIO.setmode(GPIO.BCM)
    # Setup pin 4 to accept GPIO input from touch sensor
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event listener for touch sensor GPIO pin
    GPIO.add_event_detect(4, GPIO.BOTH, GPIO_callback)

    # Throw main thread into action loop
    while True:
        ms_since_last_press = round(time.time() * 1000) - last_press

        if action and ms_since_last_press > 200:
            print(action + ' press.')

            if action == 'single':
                M.identify()
            elif action == 'double':
                M.add_person(str(uuid.uuid4()))

            action = None

# if __name__ == "__main__":
#     M = MainProcess(display=True)
# M.add_person("Zachary")
# M.identify()
