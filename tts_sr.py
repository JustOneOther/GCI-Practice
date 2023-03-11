from random import choice
import speech_recognition as sr
import pyttsx3


# -------- Text to speech --------

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 200)


def tts_set_speed(speed: int) -> None:
	tts_engine.setProperty('rate', speed)


def tts_say(phrase: str) -> None:
	tts_engine.setProperty('voice', choice(tts_engine.getProperty('voices')).id)
	tts_engine.say(phrase)
	tts_engine.runAndWait()
	tts_engine.stop()


# -------- Speech recognition --------

class SRHandler:
	def __init__(self):
		self.recognizer = sr.Recognizer()
		self.microphone = sr.Microphone()
		self.microphones = sr.Microphone.list_microphone_names()
