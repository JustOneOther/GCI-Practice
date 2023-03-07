from threading import Lock
import re


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
		if aspect:
			self.aspect = aspect.strip()
		else:
			self.aspect = None
		if cardinal:
			self.cardinal = cardinal.strip()
		else:
			self.cardinal = None

	def __str__(self):
		return f'{self.bearing}, {self.dist}, {self.altitude}, {self.heading}, {self.aspect}, {self.cardinal}'


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


class Response:
	"""Finds problem-relevant aspects of phrase and checks its format agains form"""
	def __init__(self, phrase: str, form: str):
		self.form = bool(re.match(form, phrase))
		if ident := re.search(r'([a-z]+) (\d)-\d ([a-z]+)', phrase):		# Searches for id phrase (sign, num-1, alias)
			self.sign = ident[1]
			self.num = int(ident[2])
			self.alias = ident[3]
		if braa := re.search(r'braa (\d{3}) (\d+)', phrase):		# Searches for and parses braa call
			if air := re.match(r' (\d+) thousand (\w+)( north\w*| south\w*)?', phrase[braa.end():]):
				self.braa = Braa(int(braa[1]), int(braa[2]), int(air[1]), None, air[2], air[3])
			else:
				self.braa = Braa(int(braa[1]), int(braa[2]), None, None, None, None)
		if bulls := re.search(r'bullseye (\d{3})(( for)? |/| )(\d+)', phrase):		# Searches for and parses bulls call
			if air := re.match(r' (at )?(\d+) thousand track( north\w*| south\w*)', phrase[bulls.end():]):		# Checks if bulls is for an air element
				self.bulls = Braa(int(bulls[1]), int(bulls[4]), int(air[2]), None, None, air[3])
			else:
				self.bulls = Bulls(int(bulls[1]), int(bulls[4]), None, None)
		if contact := re.search(r'standby|(\w+) contact', phrase):		# Searches for recognition of plane (sby, rdr/neg contact)
			self.contact = (contact[1] == 'radar')
		if sam := re.search(r'caution (\S+)', phrase):
			self.sam_type = sam[1]
		if state := re.search(r'(\d \d \d) (\+|-|plus|minus) (\d+(\.|,)\d)', phrase):
			self.foxs = [int(i) for i in state[1].split(' ')]
			self.guns = (state[2] in ['+', 'plus'])
			self.fuel = int(state[3].replace(state[4], ''))
		if mission := re.search(r'(single|[2-4]) ship (\S+) for (\w+)', phrase):
			self.plane_count = mission[1]
			self.model = mission[2].lower()
			self.mission = mission[3]

	def __getattr__(self, item):
		return None

	def __str__(self):
		return f'{self.sign}, {self.num}, {self.alias}, {self.braa}, {self.bulls}, {self.contact}, {self.form}'


class TranslateDict(dict):
	"""
		Based off of dict, returns key if key is undefined
	"""
	@staticmethod
	def __missing__(key):
		return key
