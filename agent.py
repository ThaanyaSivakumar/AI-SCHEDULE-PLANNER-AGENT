import speech_recognition as sr
import pyttsx3
import sqlite3
import threading
import time
import re
import os
from datetime import datetime
from playsound import playsound
from win10toast import ToastNotifier

# ---------------- SETUP ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)

toaster = ToastNotifier()

DB = "planner.db"
ALARM = "alarm.mp3"
MOTIVATION = "motivation.mp3"

# ---------------- VOICE OUTPUT ----------------
def speak(text):
    print("Planner:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- NOTIFICATION ----------------
def notify(title, message):
    try:
        toaster.show_toast(
            title,
            message,
            duration=10,
            threaded=True
        )
    except Exception as e:
        print("Notification error:", e)

# ---------------- DATABASE ----------------
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        time TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        time TEXT
    )
    """)

    con.commit()
    con.close()

# ---------------- TIME PARSER ----------------
def parse_time(text):
    text = text.lower().replace(".", "")
    match = re.search(r'(\d{1,2})(?::|\s)?(\d{2})?\s?(am|pm)', text)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm = match.group(3)

    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"

# ---------------- REMINDER CHECKER ----------------
def reminder_checker():
    while True:
        now = datetime.now().strftime("%H:%M")

        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id, task FROM reminders WHERE time=?", (now,))
        rows = cur.fetchall()

        for r in rows:
            task = r[1]
            speak(f"Reminder. {task}")
            notify("Schedule Planner", f"Reminder: {task}")

            if os.path.exists(ALARM):
                try:
                    playsound(ALARM)
                except:
                    pass

            cur.execute("DELETE FROM reminders WHERE id=?", (r[0],))
            con.commit()

        con.close()
        time.sleep(30)

# ---------------- VOICE INPUT ----------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except:
        return ""

# ---------------- COMMAND PROCESSOR ----------------
def process_command(text):
    # MOTIVATION
    if any(w in text for w in ["tired", "depress", "sad", "stressed"]):
        msg = "This feeling is temporary. You are stronger than you think. Victory starts now."
        speak(msg)
        notify("Motivation", msg)

        if os.path.exists(MOTIVATION):
            try:
                playsound(MOTIVATION)
            except:
                pass
        return

    # REMINDER
    if "remind me" in text:
        t = parse_time(text)
        if not t:
            speak("Please say the time clearly like 4 15 PM")
            return

        task = text.split(" at ")[0].replace("remind me to", "").strip()

        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT INTO reminders(task,time) VALUES (?,?)", (task, t))
        con.commit()
        con.close()

        speak(f"Reminder set for {t}")
        notify("Schedule Planner", f"Reminder set: {task} at {t}")
        return

    # SCHEDULE TASK
    if "schedule" in text:
        t = parse_time(text)
        if not t:
            speak("Please say the time clearly like 5 PM")
            return

        task = text.split(" at ")[0].replace("schedule", "").strip()

        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT INTO tasks(task,time) VALUES (?,?)", (task, t))
        con.commit()
        con.close()

        speak(f"Task scheduled at {t}")
        notify("Schedule Planner", f"Task scheduled: {task} at {t}")
        return

    speak("I did not understand. You can say schedule or remind me.")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    threading.Thread(target=reminder_checker, daemon=True).start()

    speak("Hello. I am your Schedule Planner.")

    while True:
        print("\nPress ENTER for voice or type command:")
        cmd = input("Speak or type: ").strip()

        if cmd == "":
            cmd = listen()

        if cmd in ["exit", "quit", "stop"]:
            speak("Goodbye")
            break

        process_command(cmd)
