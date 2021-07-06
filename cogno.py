from Recognition import FacialIdentifier, SpeechRecognition
from multiprocessing import Process, Pipe
import logging
import time

class MainProcess():
    def __init__(self):
        self.Face = FacialIdentifier()
    def identify(self):
        pass
    def add_person(self):
        pass
if __name__ == "__main__":
    M = MainProcess()
