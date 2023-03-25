try:
	from random import choice
	import pyttsx3
except ImportError as error:
	from time import sleep
	print('Make sure that you\'ve imported all required packages.')
	print("If they are installed correctly, please use send the following to #bugs in Damsel's server:")
	print(type(error), '|', error.args)
	sleep(20)
	raise ImportError


tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 200)


def tts_set_speed(speed: int) -> None:
	tts_engine.setProperty('rate', speed)


def tts_say(phrase: str) -> None:
	tts_engine.setProperty('voice', choice(tts_engine.getProperty('voices')).id)
	tts_engine.say(phrase)
	tts_engine.runAndWait()
	tts_engine.stop()
