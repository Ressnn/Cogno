import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib

HOST=''
PORT=8485

# Create, bind, and listen on a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(10)

conn, addr = s.accept()

handler = ServerHandler()

while True:
    # 1 for identification, 2 for addition
    instruction = int.from_bytes(conn.recv(4), 'little')

    # Read size of image and declare empty byte array for image data
    size = int.from_bytes(conn.recv(4), 'little')
    img = b''

    # Read image in 4096 bytes at a time
    for _ in range(size // 4096):
        img += conn.recv(4096)

    # Read the last nugget of the image and turn it into a numpy array
    img += conn.recv(size % 4096)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    if instruction == 1:
        # Get the handler to identify the person
        uuid = handler.identify(img)

        # Send back the length of the UUID string as well as the string itself
        conn.send(len(uuid).to_bytes(4, 'little'))
        conn.send(uuid)
    elif instruction == 2:
        # Read in the UUID string
        uuid_len = int.from_bytes(conn.recv(4), 'little')
        uuid = str(conn.recv(uuid_len))

        # Get handler to add person to deepface database
        handler.add_person(img, uuid)

        # Send back acknoledgement
        conn.send((44).to_bytes(4, 'little'))
    else:
        print(f'Unrecognized command: {instruction}.')
    
    
