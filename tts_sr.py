from random import choice
from threading import Lock
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
		self.microphone_list = sr.Microphone.list_microphone_names()

		self.stopper = None
		self.audio_buffer = []				# Stores audio frame data
		self.audio_lock = Lock()			# Audio buffer lock

	# ---------- Audio recording ----------

	def _store_audio(self, recognizer, audio_data: sr.AudioData):		# !!! - - - Called from a seperate thread - - - !!!
		with self.audio_lock:
			self.audio_buffer.append(audio_data.frame_data)

	def _stop_recording(self):
		self.stopper()
		with self.audio_lock:
			return sr.AudioData(b"".join(self.audio_buffer), self.microphone.SAMPLE_RATE, self.microphone.SAMPLE_WIDTH)

	# ---------- Audio parsing ----------
	def _parse_str(self, words: str):
		out = words
		return out

	# ---------- Interface ----------

	def get_words(self) -> str:
		if self.stopper is None:
			return 'nw_error'
		self.stopper = None

		audio = self._stop_recording()
		try:
			words = self.recognizer.recognize_sphinx(audio)
		except sr.UnknownValueError:
			return 'uw_error'

		return self._parse_str(words)

	def start_recording(self):
		with self.audio_lock:
			self.audio_buffer = []
		self.stopper = self.recognizer.listen_in_background(self.microphone, self._store_audio)

