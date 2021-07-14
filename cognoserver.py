from Recognition import FacialIdentifier
from pydub.playback import play
import struct
import pickle
import socket
import cv2

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

        #sounds = os.listdir(os.path.join(self.a_path,str(id)))
        #fp os.path.join(os.path.join(self.a_path,str(id)),sounds[0])
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

while True:
    conn, addr = s.accept()

    # 1 for identification, 2 for addition
    instruction = int.from_bytes(conn.recv(4), 'little')

    # Read size of image and declare empty byte array for image data
    img = cv2.imdecode(recv_block(), cv2.IMREAD_COLOR)

    if instruction == 1:
        # Get the handler to identify the person
        uuid = handler.identify(img)

        # Send back the length of the UUID string as well as the string itself
        conn.sendall(len(uuid).to_bytes(4, 'little'))
        conn.sendall(uuid.encode())

        print('Found person with UUID: ' + uuid)

        sound = recv_block()
        play(sound)
    elif instruction == 2:
        # Read in the UUID string
        uuid_len = int.from_bytes(conn.recv(4), 'little')
        uuid = conn.recv(uuid_len).decode('utf-8')

        print('Received addition instruction with UUID: ' + uuid)

        # Get handler to add person to deepface database
        handler.add_person(img, uuid)

        # Send back acknoledgement
        # conn.send((44).to_bytes(4, 'little'))
    else:
        print(f'Unrecognized command: {instruction}.')
    