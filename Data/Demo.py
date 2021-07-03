
from deepface import DeepFace
import pandas as pd


class FacialIdentifier():
    def __init__(self):
        self.ID = DeepFace.stream(r"C:\Users\ASUS\Documents\Cogno\Data\facebase")

FacialIdentifier()
