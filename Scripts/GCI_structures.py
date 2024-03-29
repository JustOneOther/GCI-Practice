try:
	import re
except ImportError as err:
	from time import sleep
	print('Please make sure you have all packages installed')
	print('If you do, please send the following information to #bugs in Damsel\'s server:')
	print(type(err), '|', err.args)
	sleep(20)
	raise Exception('Installation error')


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


class Response:
	"""Finds problem-relevant aspects of phrase and checks its format agains form"""
	def __init__(self, phrase: str, form: str):
		self.form = bool(re.match(form, phrase))
		if ident := re.search(r'([a-z]+) (\d)-\d ([a-z]+)', phrase):		# Searches for id phrase (sign, num-1, alias)
			self.sign = ident[1]
			self.num = int(ident[2])
			self.alias = ident[3]
		if braa := re.search(r'braa (\d{3})( |/)(\d+)', phrase):		# Searches for and parses braa call
			if air := re.match(r' (\d+) thousand (\w+)( north\w*| south\w*)?', phrase[braa.end():]):
				self.braa = Braa(int(braa[1]), int(braa[3]), int(air[1]), None, air[2], air[3])
			else:
				self.braa = Braa(int(braa[1]), int(braa[3]), None, None, None, None)
		if bulls := re.search(r'(bullseye|b/e) (\d{3})( for |/| )(\d+)', phrase):		# Searches for and parses bulls call
			if air := re.match(r' (at )?(\d+) thousand track( north\w*| south\w*)', phrase[bulls.end():]):		# Checks if bulls is for an air element
				self.bulls = Braa(int(bulls[2]), int(bulls[4]), int(air[2]), None, None, air[3])
			else:
				self.bulls = Bulls(int(bulls[2]), int(bulls[4]), None, None)
		if contact := re.search(r'standby|(\w+) contact', phrase):		# Searches for recognition of plane (sby, rdr/neg contact)
			self.contact = (contact[1] == 'radar')
		if sam := re.search(r'caution (\S+)', phrase):
			self.sam_type = sam[1]
		if state := re.search(r'(\d \d \d) (\+|-|plus|minus) (\d+(\.|,)\d)', phrase):
			self.foxs = [int(i) for i in state[1].split(' ')]
			self.guns = (state[2] in {'+', 'plus'})
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
