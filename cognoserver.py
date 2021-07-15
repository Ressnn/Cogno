from Recognition import FacialIdentifier
from playsound import playsound
import struct
import pickle
import socket
import cv2
import uuid
import pyaudio
from collections import deque
import threading
import wave
import os

class ServerHandler():
    def __init__(self, facebase_path="./Data/facebase"):
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
        self.Face = FacialIdentifier(dbpath=facebase_path)
        self.f_path = facebase_path

    def identify(self, image):
        """
        Identifies ther person in the frame and repeats the name back in the user's ear

        Returns
        -------
        Boolean
            True if face was discovered False if otherwise

        """

        image = cv2.flip(image, 0)

        try:
            id = self.Face.get_person(image, prob_threshold=1)
            print(id)
        except:
            print("No Face in Frame")
            return False

        if id == -1:
            return False
        
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

        image = cv2.flip(image, 0)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.Face.add_face(image, name)

class AudioBuffer():
    def __init__(self, dbpath, seconds=3):
        """
        An audiobuffer that keeps the last few seconds of audio in memory

        Parameters
        ----------
        dbpath : String
            The path to the audiobase.
        seconds : float or int
            The the amount of time to keep in memory

        Returns
        -------
        NoneType
            None

        """

        self.dbpath = dbpath
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = seconds

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index=0
        )

        self.frames = deque()

        try:
            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)
        except:
            pass

        self.AudioThread = threading.Thread(target=self._read_loop, args=())
        self.AudioThread.start()

    def read(self):
        """
        Reads another moment of the audio and adds it to the buffer whiled popleft() in the last second

        Returns
        -------
        NoneType
            None

        """
        data = self.stream.read(self.CHUNK)
        self.frames.append(data)
        self.frames.popleft()

    def _read_loop(self):
        """
        Loops the read function

        Returns
        -------
        NoneType
            None

        """
        while True:
            self.read()

    def get(self):
        """
        Gets the last few seconds of the audiobuffer

        Returns
        -------
        deque
            A deque with raw audio data from PyAudio

        """
        return self.frames

    def close(self):
        """
        Closes the pyaudio stream and stops recording

        Returns
        -------
        NoneType
            None

        """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def save(self, name):
        """
        Saves the audiostream to a file under the audiobase with a folder called "name"

        Parameters
        ----------
        name : str
            Name to save the folder under in the audiobase

        Returns
        -------
        NoneType
            None

        """

        wf = wave.open(os.path.join(self.dbpath, name + '.wav'), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(list(self.frames)))
        wf.close()

HOST=''
PORT=8485

def recv_block():
    data = b''
    payload_size = struct.calcsize('>L')

    while len(data) < payload_size:
        data += conn.recv(4096)
    
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]

    msg_size = struct.unpack('>L', packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)
    
    frame_data = data[:msg_size]
    data = data[msg_size:]

    return pickle.loads(frame_data, fix_imports=True, encoding='bytes')

# Create, bind, and listen on a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(10)

handler = ServerHandler()
audio_buffer = AudioBuffer('Data/audiobase')

while True:
    conn, addr = s.accept()

    # 1 for identification, 2 for addition
    instruction = 'single' if int.from_bytes(conn.recv(4), 'little') == 1 else 'double'
    img = cv2.imdecode(recv_block(), cv2.IMREAD_COLOR)

    if instruction == 'single':
        # Get the handler to identify the person
        id = handler.identify(img)

        if not id:
            print('No person found in frame.')
            continue

        print(f'Found person with id: {id}')
        print('Playing audio...')

        playsound(f'{os.path.join(audio_buffer.dbpath, id)}.wav')

        print('Done playing audio.')
    elif instruction == 'double':
        # Get handler to add person to deepface database
        id = str(uuid.uuid4())
        audio_buffer.save(id)
        handler.add_person(img, id)

        print(f'Added person with id: {id}')
    else:
        print(f'Unrecognized command: {instruction}.')
    