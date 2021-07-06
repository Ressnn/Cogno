
from Recognition import FacialIdentifier, SpeechRecognition
from multiprocessing import Process, Pipe
import logging
import time

class MainThreadWorker():
    def __init__(self):
        logging.info("Main Process Started")
        self._kickoff_workers()

    def _kickoff_workers(self):
        logging.info("Starting Child Processes")
        F,S = self._generate_pipes()
        self.FaceProcess = FacialRecognitionChildProcess(F)
        self.SpeechProcess = SpeechRecognitionChildProcess(S)

        self.FaceProcess.start()
        self.SpeechProcess.start()

    def _generate_pipes(self):
        self.FaceProcessPipe, givetoF = Pipe()
        self.SpeechProcessPipe, givetoS = Pipe()
        return givetoF,givetoS

    def main_loop():
        pass

class FacialRecognitionChildProcess(Process):
    def __init__(self,pipe):
        super(Process, self).__init__()
        self.FaceCog = FacialIdentifier()
        self.mainpipe = pipe
        logging.info("Facial Recognition Process Started")
    def run(self):
        while True:
            print("HI")

class SpeechRecognitionChildProcess(Process):
    def __init__(self,pipe):
        super(Process, self).__init__()
        self.SpeechCog = FacialIdentifier()
        self.mainpipe = pipe
        logging.info("Voice Recognition Process Started")
    def run(self):
        while True:
            pass



if __name__ == '__main__':
    M = MainThreadWorker()
    time.sleep(1)
    print(M.FaceProcess.is_alive())
    print(M.SpeechProcess.is_alive())
