from Recognition import FacialIdentifier, AudioBuffer
from multiprocessing import Process, Pipe
import logging
import time
import os
from playsound import playsound
import uuid
import cv2


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

if __name__ == "__main__":
    M = MainProcess(display=True)
M.add_person("Zachary")
M.identify()
