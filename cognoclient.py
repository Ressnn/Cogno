import RPi.GPIO as GPIO
import cv2
import socket
import time
import struct
import pickle

# Global variable specifically for server connection
client_socket = None

def connect_server():
    global client_socket

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.5', 8485))

def close_connection():
    global client_socket

    client_socket.close()
    client_socket = None

# Global variables used specifically for GPIO callback
GPIO_action = None
last_press = 0

def GPIO_callback(channel):
    global GPIO_action, last_press

    print('GPIO action detected.')

    press_time = round(time.time() * 1000)
    press_diff = press_time - last_press

    last_press = press_time
    GPIO_action = 'double' if press_diff < 250 else 'single'

def send_block(data):
    data = pickle.dumps(data, 0)
    size = len(data)

    client_socket.sendall(struct.pack(">L", size) + data)

if __name__ == '__main__':
    camera = cv2.VideoCapture(0)

    # Set GPIO mode to BCM (not sure what it means but it works)
    GPIO.setmode(GPIO.BCM)
    # Setup pin 4 to accept GPIO input from touch sensor
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event listener for touch sensor GPIO pin
    GPIO.add_event_detect(17, GPIO.BOTH, GPIO_callback)

    # Throw main thread into action loop
    while True:
        ms_since_last_press = round(time.time() * 1000) - last_press

        if GPIO_action and ms_since_last_press > 200:
            connect_server()
            print(GPIO_action + ' press.')

            # Send instruction (1 for single press, 2 for double press)
            instruction = 1 if GPIO_action == 'single' else 2
            client_socket.send(instruction.to_bytes(4, 'little'))

            send_block(cv2.imencode('.jpg', camera.read()[1])[1])

            GPIO_action = None
            close_connection()

            print('Closed server connection.')
