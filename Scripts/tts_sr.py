try:
	from Scripts.GCI_structures import TranslateDict
	from io import BytesIO
	from random import choice
	from re import sub
	from threading import Lock, Thread
	import pocketsphinx as ps
	import pyaudio
	import pyttsx3
except ImportError as err:
	from time import sleep
	print('Please make sure you have all packages installed')
	print('If you do, please send the following information to #bugs in Damsel\'s server:')
	print(type(err), '|', err.args)
	sleep(20)
	raise Exception('Installation error')


# -------- Text to speech --------

tts_engine = pyttsx3.init()


def tts_set_speed(new_speed: int) -> None:
	tts_engine.setProperty('rate', new_speed)
	tts_engine.runAndWait()


def tts_say(phrase: str, speed: int) -> None:
	tts_engine.setProperty('voice', choice(tts_engine.getProperty('voices')).id)
	tts_engine.setProperty('rate', speed)
	tts_engine.say(phrase)
	tts_engine.runAndWait()


# -------- Speech recognition --------


class Microphone:
	def __init__(self):
		self.audio = pyaudio.PyAudio()
		self.mic_info = self.audio.get_default_input_device_info()
		self.rec_format = pyaudio.paInt16
		self.chunk_size = 2048
		self.sample_rate = int(self.mic_info["defaultSampleRate"])
		self.fps = self.sample_rate / self.chunk_size

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
		try:		# Might throw an error if close_stream is called, idk
			self.audio_stream.close()
			self.audio_stream = None
		finally:
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
		self.audio_data = b''			# Could be replaced by out_byes, but thread safety

		self.config = ps.Config(lm=None, dict=None)
		self.config['lm'] = 'Resources/lang_model/0889.lm'
		self.config['dict'] = 'Resources/lang_model/0889.dic'
		self.config['samprate'] = self.mic.sample_rate
		self.config['frate'] = 150
		self.decoder = ps.Decoder(self.config)

		self.audio_dict = TranslateDict(ZERO='0', ONE='1', TWO='2', THREE='3', FOUR='4', FIVE='5', SIX='6', SEVEN='7',
										EIGHT='8', NINER='9', TEN='10', ELEVEN='11', TWELVE='12', THIRTEEN='13', FOURTEEN='14',
										FIFTEEN='15', SIXTEEN='16', SEVENTEEN='17', EIGHTEEN='18', NINETEEN='19', TWENTY='2',
										THIRTY='3', FORTY='4', FIFTY='5', SIXTY='6', SEVENTY='7', EIGHTY='8', NINETY='9',
										BRA='BRAA', BULLSEYE='B/E',FLANK='flanking', BEAM='beaming', DRAGGING='drag',
										DECIMAL='.', BYE='BAI', SEED='SEAD', J_F='jf', S_A='SA')
		self.compound_num = {'TWENTY', 'THIRTY', 'FORTY', 'FIFTY', 'SIXTY', 'SEVENTY', 'EIGHTY', 'NINETY'}
		self.compound_plane = {'F', 'J_F', 'S_A'}

	# ---------- Mic recording ----------

	def start_recording(self):
		self.rec_on = True
		self.rec_thread = Thread(target=self._record_audio)
		self.rec_thread.start()

	def stop_recording(self):
		with self.rec_lock:
			self.rec_on = False
		self.rec_thread.join()
		self.audio_data = self.out_bytes
		self.rec_thread = None

	def _record_audio(self):			# !!! - - - Called from a non-main thread - - - !!!
		buffer = BytesIO()
		with self.mic:
			while True:
				buffer.write(self.mic.read_chunk())
				self.rec_lock.acquire()			# Faster than context manager? Idk, but it might help
				if not self.rec_on:
					self.rec_lock.release()
					break
				self.rec_lock.release()
		self.out_bytes = buffer.getvalue()
		buffer.close()

	# ---------- Speech recognition ----------

	def recognize_audio(self) -> str:
		self.decoder.start_utt()
		self.decoder.process_raw(self.audio_data)
		self.decoder.end_utt()
		return self._parse_raw(self.decoder.seg())

	def _parse_raw(self, segments: ps.Segment) -> str:
		words = []
		cont_flag = False
		for seg in segments:
			word = sub('\(\d\)', '', seg.word)
			if cont_flag == 'num':			# Handle compound numbers
				if word in {'<s>', '</s>', '<sil>', '[NOISE]', '[SPEECH]'}:
					words[-1] += '0'
				elif word in self.compound_num:
					words[-1] += '0'
					words.append(self.audio_dict[word])
					continue
				else:
					words[-1] += self.audio_dict[word]
				cont_flag = False
			elif cont_flag == 'plane':		# Handle compound plane/sam names
				if word in {'<s>', '</s>', '<sil>', '[NOISE]', '[SPEECH]'}:
					continue
				words[-1] += '-' + self.audio_dict[word]
				cont_flag = False
			elif word in {'<s>', '</s>', '<sil>', '[NOISE]', '[SPEECH]'}:		# Handle silence or undetermined speech
				continue
			else:			# Handle standard words
				words.append(self.audio_dict[word])
				if word in self.compound_plane:
					cont_flag = 'plane'
				if word in self.compound_num:
					cont_flag = 'num'
		out_raw = ' '.join([word.lower() for word in words])			# Create out string
		return out_raw.replace(' . ', '.').replace('. ', '0.')			# Fix decimals and compound number decimals

