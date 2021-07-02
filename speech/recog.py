import speech_recognition as sr

KEY_PHRASES = ["my name is ", "i'm ", "i am "]

def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    text = recognizer.recognize_google(audio).lower()
    print(text)

    for phrase in KEY_PHRASES:
        start_name = text.find(phrase)
        if start_name == -1:
            continue
        
        start_name += len(phrase)

        end_name = text.find(' ', start_name)
        end_name = len(text) if end_name == -1 else end_name
        
        return text[start_name:end_name]

    return None
