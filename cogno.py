from Recognition import FacialIdentifier, AudioBuffer
from multiprocessing import Process, Pipe
from playsound import playsound
#import RPi.GPIO as GPIO
import logging
import time
import uuid
import cv2
import os

# if __name__ == "__main__":
#     M = MainProcess(display=True)
# M.add_person("Zachary")
# M.identify()
