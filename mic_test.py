import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 160)

def speak(text):
    print("Planner:", text)
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    speak("Hello, I am your planner. Say something.")
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)

try:
    command = recognizer.recognize_google(audio)
    print("You said:", command)

    if "planner" in command.lower():
        speak("Yes, I am listening. How can I help you?")
    else:
        speak("I heard you.")

except:
    speak("Sorry, I could not understand.")
