import cv2
import socket
import time
import pyaudio
from playsound import playsound
import wave
import uuid
from collections import deque
import os
import threading
import RPi.GPIO as GPIO

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
        self.CHUNK = 2048
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
            input_device_index=1
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
        try:
            os.mkdir(os.path.join(self.dbpath, name))
        except:
            pass

        wf = wave.open(os.path.join(self.dbpath, name, str(uuid.uuid4()) + ".wav"), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(list(self.frames)))
        wf.close()


# Global variable specifically for server connection
client_socket = None

def connect_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.5', 8485))


# Global variables used specifically for GPIO callback
GPIO_action = None
last_press = 0

def GPIO_callback(channel):
    global GPIO_action, last_press

    press_time = round(time.time() * 1000)
    press_diff = press_time - last_press

    last_press = press_time
    GPIO_action = 'double' if press_diff < 250 else 'single'


if __name__ == '__main__':
    camera = cv2.VideoCapture(0)

    # Initialize audio buffer
    audio_buffer = AudioBuffer('Data/audiobase')

    # Set GPIO mode to BCM (not sure what it means but it works)
    GPIO.setmode(GPIO.BCM)
    # Setup pin 4 to accept GPIO input from touch sensor
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event listener for touch sensor GPIO pin
    GPIO.add_event_detect(4, GPIO.BOTH, GPIO_callback)

    # Throw main thread into action loop
    while True:
        ms_since_last_press = round(time.time() * 1000) - last_press

        if GPIO_action and ms_since_last_press > 200:
            connect_server()
            print(GPIO_action + ' press.')

            if GPIO_action == 'double':
                # Create new UUID and save audio file under that name
                id = str(uuid.uuid4())
                audio_buffer.save(id)

                # Read single camera frame
                _, img = camera.read()
                img = cv2.imencode('.jpg', img).tobytes()

                # Send the image along with its length
                client_socket.send(len(img).to_bytes(4, 'little'))
                client_socket.send(img)

                # Send the UUID along with its length
                client_socket.send(len(id).to_bytes(4, 'little'))
                client_socket.send(id)
            elif GPIO_action == 'single':
                # Capture a frame and encode it in JPEG
                _, img = camera.read()
                img = cv2.imencode('.jpg', img).tobytes()

                # Send the image across the socket with its size
                client_socket.send(len(img).to_bytes(4, 'little'))
                client_socket.send(img)

                # Read UUID from server
                id_len = int.from_bytes(client_socket.read(4), 'little')
                id = str(client_socket.read(id_len))

                # Play sound from saved wav file
                playsound(id + '.wav')

            GPIO_action = None
