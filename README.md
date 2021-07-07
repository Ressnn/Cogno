![cognologo](https://github.com/Ressnn/Cogno/blob/main/Data/assets/logos/cogno_white.jpg)

# Cogno

Have you ever forgotten someone's name that you should know and been embarrassed when you have to ask for their name? Made during [GHP 58](https://gosa.georgia.gov/governors-honors-program) for our final engineering project, Cogno is the solution to that universal problem. When meeting someone and hearing their name for the first time, simply double-tap the side of the Cogno glasses and Cogno will intelligently record the last couple seconds of your conversation so that pronunciation is perfectly preserved. Later, when you need Cogno to recall the name, simply single-tap the side instead, and the glasses will recognize the face of the person you are speaking to and play their name, exactly as they said it originally, back into your ear. Cogno is meant to be an invisible solution, so it is mounted on an ordinary pair of glasses with a small camera and microphone. Even when using Cogno, it is unlikely that a person would be able to discern that a name-remembering aid is being used at all.

## How it works

Cogno integrates a camera/microphone pair onto an ordinary-looking pair of glasses to provide a great user experience. Currently, the preferred method for name repetition is into the user's own headphones, but in the future, we hope that we can integrate small bone-conduction speakers into the back of the glasses so headphones will no longer be necessary. As for the technology, Cogno uses a Raspberry Pi 4 to connect the devices and perform facial recognition, which will invisibly sit in your pocket. Several open-source libraries are used throughout the program, such as *deepface* and *pyaudio* for facial recognition and audio recording and playback, respectively. Beyond that, all Cogno source is public and licensed under the [MIT License](LICENSE), so feel free to explore the source code!

## The Team

- Pranav Devarinti (Computer Science): *"nothing ever works on arm."*

- Zach Hames (Mechatronic Engineering): *"the lead from the solder has fried my brain cells."*

- Jeffrey Shelton (Computer Science): *"i wish we wrote this in c."*

## Privacy

Cogno is extremely privacy-cognizant, and it takes several measures to avoid recording you any more than necessary. The camera and microphone are only activated and recording only the user indicates they should by single- or double-tapping the touch sensor on the side of the glasses. No data is sent off-device to be processed or stored by a server, a fact which can be demonstrated by Cogno's lack of dependence on internet connectivity. In short, Cogno does not pose a threat to privacy and only captures small bursts of audio and video when the user indicates it to do so.
