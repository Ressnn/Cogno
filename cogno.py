from Recognition import FacialIdentifier, AudioBuffer
from multiprocessing import Process, Pipe
from playsound import playsound
#import RPi.GPIO as GPIO
import logging
import time
import uuid
import cv2
import os

class ServerProcess():
    def __init__(self,display = False, facebase_path = "./Data/facebase", audiobase_path ="./Data/audiobase", flip_image = False):
        """
        Constructor for the MainProcess of cogno

        Parameters
        ----------
        display : Boolean
            Display Frames for Debugging?
        facebase_path : String
            path to facebase to match
        audiobase_path : String
            path to audiobase with pronunciations

        Returns
        -------
        NoneType
            None

        """
        self.flip = flip_image
        self.Face = FacialIdentifier(dbpath=facebase_path)
        self.AudioProcess = AudioBuffer(dbpath=audiobase_path)
        self.display = display
        self.f_path = facebase_path
        self.a_path = audiobase_path

    def identify(self, image):
        """
        Identifies ther person in the frame and repeats the name back in the user's ear

        Returns
        -------
        Boolean
            True if face was discovered False if otherwise

        """

        frame = image
        if self.flip == True:
            frame = cv2.flip(frame,0)

        if self.display == True:
            cv2.imshow('frame', frame)
        try:
            id = self.Face.get_person(frame,prob_threshold=1)
            print(id)
        except:
            print("No Face in Frame")
            return False

        if id == -1:
            return False

        #sounds = os.listdir(os.path.join(self.a_path,str(id)))
        #fp os.path.join(os.path.join(self.a_path,str(id)),sounds[0])
        return str(id)

    def add_person(self, image, name):
        """
        Adds a person to the audio and facebase

        Parameters
        ----------
        name : String
            The name to store a person by in the databases

        Returns
        -------
        NoneType
            None

        """
        frame = self.vid.read()

        if self.flip == True:
            frame = cv2.flip(frame,0)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.Face.add_face(frame,name)
        
# if __name__ == "__main__":
#     M = MainProcess(display=True)
# M.add_person("Zachary")
# M.identify()
