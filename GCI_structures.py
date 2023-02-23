from threading import Lock


class Bulls:
	def __init__(self, bearing, dist, altitude, heading):
		self.bearing = bearing
		self.dist = dist
		self.altitude = altitude
		self.heading = heading
		self.readable = '0' * (3 - len(str(bearing))) + str(bearing)

	def __str__(self):
		return f'{self.bearing}, {self.dist}, {self.altitude}, {self.heading}'


class Braa(Bulls):
	def __init__(self, bearing, dist, altitude, heading, aspect, cardinal):
		super().__init__(bearing, dist, altitude, heading)
		self.aspect = aspect
		self.cardinal = cardinal


class LockVal:
	"""
		A variable with a built-in threading.Lock
		Value is held in .val property
	"""
	def __init__(self, val):
		self.lock = Lock()
		self.value = val

	@property
	def val(self):
		with self.lock:
			return self.value

	@val.setter
	def val(self, new_val):
		with self.lock:
			self.value = new_val


class TranslateDict(dict):
	"""
		Based off of dict, returns key if key is undefined
	"""
	@staticmethod
	def __missing__(key):
		return key
