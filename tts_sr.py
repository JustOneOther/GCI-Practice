from io import BytesIO
from random import choice
from threading import Lock, Thread
from time import sleep
import pocketsphinx as ps
import speech_recognition as sr
import tomllib as tom
import pyaudio
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


class Microphone:
	def __init__(self):
		self.audio = pyaudio.PyAudio()
		self.mic_info = self.audio.get_default_input_device_info()
		self.rec_format = pyaudio.paInt16
		self.chunk_size = 2048
		self.sample_size = pyaudio.get_sample_size(self.rec_format)
		self.sample_rate = int(self.mic_info["defaultSampleRate"])

		self.audio_stream = None

		self.audio.terminate()

	# ---------- Context manager bits ----------

	def __enter__(self):
		assert self.audio_stream is None, "An audio stream is already open"
		self.audio = pyaudio.PyAudio()
		self.audio_stream = self.audio.open(rate=self.sample_rate, channels=1, format=self.rec_format, input=True,
											input_device_index=None, frames_per_buffer=self.chunk_size)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.audio_stream.close()
		self.audio_stream = None
		self.audio.terminate()

	# ---------- Reading and stopping stuff ----------

	def read_chunk(self):
		return self.audio_stream.read(self.chunk_size)

	def close_stream(self):
		self.audio_stream.stop_stream()
		self.audio_stream.close()


class PySRHandler:
	def __init__(self):
		self.mic = Microphone()

		self.rec_lock = Lock()
		self.rec_on = False
		self.rec_thread = None
		self.out_bytes = b''			# Doesn't need a lock because is only read from after .join()

	# ---------- Mic recording ----------

	def start_recording(self):
		self.rec_on = True
		self.rec_thread = Thread(target=self._record_audio)
		self.rec_thread.start()

	def stop_recording(self):
		with self.rec_lock:
			self.rec_on = False
		self.rec_thread.join()

	def _record_audio(self):			# !!! Called from a non-main thread !!!
		buffer = BytesIO()
		with self.mic:
			while True:
				buffer.write(self.mic.read_chunk())
				self.rec_lock.acquire()			# Faster than context manager? Idk, but it might help
				if not self.rec_on:
					break
				self.rec_lock.release()
		self.out_bytes = buffer.getvalue()
		buffer.close()

	# ---------- Speech recognition ----------

	def recognize_audio(self):
		pass


class SRHandler:
	def __init__(self):
		self.recognizer = sr.Recognizer()
		self.microphone = sr.Microphone()
		print('A moment of silence please...')
		sleep(1)		# Give time for user to react
		with self.microphone as mic:
			self.recognizer.adjust_for_ambient_noise(mic)
		print('Microphone is calibrated!')
		self.microphone_list = sr.Microphone.list_microphone_names()

		with open('Resources/dictionary.toml', 'rb') as file:
			words_dict = tom.load(file)
		self.sphinx_words = tuple(zip(words_dict.keys(), words_dict.values()))
		print(self.sphinx_words)

		self.stopper = None
		self.audio_buffer = []				# Stores audio frame data
		self.audio_lock = Lock()			# Audio buffer lock

	# ---------- Audio recording ----------

	def _store_audio(self, recognizer, audio_data: sr.AudioData):    # !!! - - - Called from a seperate thread - - - !!!
		with self.audio_lock:
			self.audio_buffer.append(audio_data)

	def _out_words(self):
		self.stopper()
		self.stopper = None
		print('3')
		with self.audio_lock:
			return [self.recognizer.recognize_sphinx(i) for i in self.audio_buffer]

	# ---------- Audio parsing ----------
	def _parse_str(self, words: str):
		out = words
		return out

	# ---------- Interface ----------

	def get_words(self) -> str:
		if self.stopper is None:
			return 'nw_error'
		print('2')
		return '|'.join(self._out_words())

	def start_recording(self):
		with self.audio_lock:
			self.audio_buffer = []
		self.stopper = self.recognizer.listen_in_background(source=self.microphone, callback=self._store_audio, phrase_time_limit=2.5)

