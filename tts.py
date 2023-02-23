from random import choice
import pyttsx3


tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 200)


def tts_set_speed(speed: int) -> None:
	tts_engine.setProperty('rate', speed)


def tts_say(phrase: str) -> None:
	tts_engine.setProperty('voice', choice(tts_engine.getProperty('voices')).id)
	tts_engine.say(phrase)
	tts_engine.runAndWait()
	tts_engine.stop()
