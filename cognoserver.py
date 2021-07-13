from Recognition import FacialIdentifier
import numpy as np
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
        conn.send(bytes(uuid, 'utf-8'))
    elif instruction == 2:
        # Read in the UUID string
        uuid_len = int.from_bytes(conn.recv(4), 'little')
        uuid = conn.recv(uuid_len).decode('utf-8')

        # Get handler to add person to deepface database
        handler.add_person(img, uuid)

        # Send back acknoledgement
        conn.send((44).to_bytes(4, 'little'))
    else:
        print(f'Unrecognized command: {instruction}.')

    conn.close()
    