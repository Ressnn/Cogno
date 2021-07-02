from deepface import DeepFace
import pandas as pd

!pip3 freeze > requirements.txt


class FacialIdentifier():
    def __init__(self):
        self.ID = DeepFace.stream(".Data/facebase")

FacialIdentifier()
