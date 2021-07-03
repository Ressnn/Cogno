from FacialRecognition import FacialIdentifier
from speech import recog
import FacialRecognition
import cv2 as cv

def run():
    rec = recog.SpeechRecognizer()
    camera = cv.VideoCapture(0)
    identifier = FacialRecognition.FacialIdentifier()

    print('Done with setup.')

    while True:
        name = rec.listen()

        if name:
            ret, frame = camera.read()
            cv.cvtColor(frame, cv.COLOR_BGR2RGB, dst=frame)
            identifier.add_face(frame, name)

            recog.notify_name_captured()

if __name__ == '__main__':
    run()
