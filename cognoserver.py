import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib

HOST=''
PORT=8485

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, addr=s.accept()

def read_image():


data = b""
payload_size = struct.calcsize(">L")
print("payload_size: {}".format(payload_size))

while True:
    # 1 for identification, 2 for addition
    instruction = int.from_bytes(data.recv(4), 'little')

    # Read size of image and declare empty byte array for image data
    size = int.from_bytes(data.recv(4), 'little')
    img = b''

    # Read image in 4096 bytes at a time
    for _ in range(size // 4096):
        img += conn.recv(4096)

    # Read the last nugget of the image and turn it into a numpy array
    img += conn.recv(size % 4096)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    if instruction == 1:
        
    elif instruction == 2:

    else:


    while len(data) < payload_size:
        print("Recv: {}".format(len(data)))
        data += conn.recv(4096)

    print("Done Recv: {}".format(len(data)))
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    print("msg_size: {}".format(msg_size))
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]


    frame = np.frombuffer(frame_data, dtype=np.uint8)
    # frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow('ImageWindow',frame)
    cv2.waitKey(1)
