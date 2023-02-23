from math import sin, cos, radians, atan2, asin, degrees, sqrt
from tts import *
from random import choice, choices, randint, uniform
from tkinter import ttk
import multiprocessing as mp
import speech_recognition as sr
import threading as thread
import tkinter as tk
import tomllib as tom
import turtle


class TranslateDict(dict):
	@staticmethod
	def __missing__(key):
		return key


class DefaultEntryBox(tk.Entry):
	def __init__(self, text: str, *args, **kwargs):
		try:
			self.default_justify = kwargs['default_justify']
			kwargs.pop('default_justify')
		except KeyError:
			self.default_justify = 'center'
		super().__init__(*args, **kwargs)
		self.config(fg='#999999', justify=self.default_justify)
		self.text = text
		self.insert(0, self.text)
		self.bind('<Enter>', func=self.on_enter)
		self.bind('<Leave>', func=self.on_exit)

	def prompt(self):
		self.insert(0, self.text)
		# noinspection PyTypeChecker
		self.config(fg='#999999', justify=self.default_justify)

	def on_enter(self, *args):
		if self.get() == self.text:
			self.delete(0, 'end')
			self.config(fg='black', justify='left')

	def on_exit(self, *args):
		if self.get() == '':
			self.insert(0, self.text)
			# noinspection PyTypeChecker
			self.config(fg='#999999', justify=self.default_justify)


# Config reading
if __name__ == '__main__':
	# Preset vars
	mission_types = ['CAP', 'BAI', 'Strike', 'SEAD']
	single_dict = {1: 'single', 2: 2, 3: 3, 4: 4}
	translate_dict = TranslateDict()
	translate_dict['9'] = 'niner'
	aspect_shorthand = {'hot': 'H', 'flanking': 'F', 'beaming': 'B', 'drag': 'D', None: 'N/A'}

	# Read config
	with open('callsigns.txt', 'r') as file:
		friendlies = file.read().split(', ')

	with open('config.toml', 'rb') as file:
		config_dict = tom.load(file)
	stt_key = config_dict['stt_key']
	alias = config_dict['alias'].lower()
	planes = list(config_dict['planes'].values())
	sam_types = list(config_dict['sams'].values())
	ground_chance = config_dict['ground_chances']


class Threat:
	"""
		Class containing basic elements for a BRAA against a ground target
		----
		Attributes:
			bearing | int [0, 355] | Bearing from origin
			dist | int [fire_range, fire_range + 10] | Range from origin
			altitude | str ['N/A']
			aspect | None
			bulls_bearing | int [0, 355] | Bearing from bullseye
			bulls_range | int [0 , origin_range + dist] | Range from bullseye
			fire_range | int [3, 15] | Fire range of threat
		"""
	def __init__(self, origin_plane):
		model = choice(sam_types)
		if model['range'] > 10:
			self.fire_range = model['range'] * 0.8
		else:
			self.fire_range = model['range']
		self.dist = round(uniform(self.fire_range, self.fire_range + 10), 1)
		self.name = model['name']
		self.sign = model['shorthand']
		bearing_off = degrees(asin(self.fire_range/self.dist)) * 0.85 // 1
		rough_bearing = randint(origin_plane.heading - bearing_off, origin_plane.heading + bearing_off)
		self.bearing = rough_bearing % 360
		self.aspect = None
		self.altitude = 'N/A'
		bullseye_stats = braa_to_bulls(origin_plane, self.bearing, self.dist)
		self.bulls_bearing = bullseye_stats[0]
		self.bulls_range = bullseye_stats[1]
		self.readable_bearing = '0' * (3 - len(str(self.bulls_bearing))) + str(self.bulls_bearing)


class BraaPlane:
	"""
	Class containing elements for a BRAA call against a plane
	----
	Attributes:
		bearing | int [0, 355] | Bearing from origin
		dist | int [5, 99] | Range from origin
		altitude | int [1, 40] | Altitude above MSL
		heading | int [0, 359] | Heading
		aspect | str | Aspect of contact
		cardinal | str | Cardinal direction of heading
		readable_bearing | str | Bearing to be understood by answers
	"""
	def __init__(self, origin_plane, track=True, dist=None, friendly=False):
		if not friendly:
			if track:
				rough_bearing = randint(origin_plane.heading - 90, origin_plane.heading + 90)
			else:
				rough_bearing = randint(origin_plane.heading - 75, origin_plane.heading + 75)
			self.bearing = rough_bearing % 360
			if track:
				if rough_bearing < origin_plane.heading - 30:
					self.heading = randint(rough_bearing + 120, rough_bearing + 180) % 360
				elif rough_bearing > origin_plane.heading + 30:
					self.heading = randint(rough_bearing - 180, rough_bearing - 120) % 360
				else:
					self.heading = randint(rough_bearing + 135, rough_bearing + 225) % 360
			else:
				self.heading = randint(0, 359)
		else:
			rough_bearing = randint(origin_plane.heading - 255, origin_plane.heading - 105)
			self.bearing = rough_bearing % 360
			self.heading = randint(0, 359)
		if dist:
			self.dist = dist
		else:
			self.dist = randint(10, 40)
		self.altitude = randint(1, 40)
		self.readable_bearing = ' '.join([i for i in ('0' * (3 - len(str(self.bearing))) + str(self.bearing))])

		rev_bearing = (self.bearing - 180) % 360
		if abs(rev_bearing - self.heading) <= 30:
			self.aspect = 'hot'
		elif abs(rev_bearing - self.heading) <= 60:
			self.aspect = 'flanking'
		elif abs(rev_bearing - self.heading) <= 120:
			self.aspect = 'beaming'
		else:
			self.aspect = 'drag'

		if self.heading >= 337.5 or self.heading < 22.5:
			self.cardinal = 'north'
		elif 22.5 <= self.heading < 67.5:
			self.cardinal = 'north east'
		elif 67.5 <= self.heading < 112.5:
			self.cardinal = 'east'
		elif 112.5 <= self.heading < 157.5:
			self.cardinal = 'south east'
		elif 157.5 <= self.heading < 202.5:
			self.cardinal = 'south'
		elif 202.5 <= self.heading < 247.5:
			self.cardinal = 'south west'
		elif 247.5 <= self.heading < 292.5:
			self.cardinal = 'west'
		elif 247.5 <= self.heading < 292.5:
			self.cardinal = 'west'
		elif 292.5 <= self.heading < 337.5:
			self.cardinal = 'north west'


class BasicPlane:
	"""
	Class containing basic elements for a Bullseye call & drawing
	----
	Attributes:
		bearing | int [0, 355] | Bearing from bullseye
		dist | int [5, 99] | Range from bullseye
		altitude | int [1, 40] | Altitude above MSL
		heading | int [0, 359] | Heading of track
		speed | float [5, 12.5] ; rounded to tenths | Speed in nautical miles per 30 seconds, multiply * 120 for knots
	"""
	def __init__(self, bearing=None, dist=None, alt=None, head=None):
		if bearing is not None:
			self.bearing = bearing
		else:
			self.bearing = randint(0, 359)
		if dist is not None:
			self.dist = dist
		else:
			self.dist = randint(5, 99)
		if alt is not None:
			self.altitude = alt
		else:
			self.altitude = randint(1, 40)
		if head is not None:
			self.heading = head
		else:
			self.heading = randint(0, 359)
		self.speed = round(uniform(5, 12.5), 1)


class NamedPlane(BasicPlane):
	"""
	Basic plane with a name for text-to-speech
	----
	Inherited Attributes:
		bearing | int [0, 355] | Bearing from bullseye
		dist | int [5, 99] | Range from bullseye
		altitude | int [1, 40] | Altitude above MSL
		heading | int [0, 359] | Heading of track
		speed | float [5, 12.5] ; rounded to tenths | Speed in nautical miles per 30 seconds, multiply * 120 for knots
	----
	Attributes:
		callsign | str | Callsign to be used by tts and sr
		flight_number | str | Flight number for answer
	"""
	def __init__(self, bearing=None, dist=None, alt=None, head=None):
		super().__init__(bearing, dist, alt, head)
		self.callsign = choice(friendlies)
		self.flight_number = str(randint(1, 9))


class LoadoutPlane(BasicPlane):
	"""
	More advanced plane with payload, fuelstate, and readable variables. Inherits from BasicPlane
	----
	Inherited Attributes:
		bearing | int [0, 355] | Bearing from bullseye
		dist | int [5, 99] | Range from bullseye
		altitude | int [1, 40] | Altitude above MSL
		heading | int [0, 359] | Heading of track
		speed | float [5, 12.5] ; rounded to tenths | Speed in nautical miles per 30 seconds, multiply * 120 for knots
	----
	Attributes:
		name | str | Name of type of plane
		callsign | str | Callsign to be used by tts and sr
		guns | str ('plus', 'minus') | If the plane is equipped with balistic weapons
		readable_bearing | str ('x x x') | Inherited bearing attribute to be read and heard correctly by tts and sr
		foxs | list[int, int, int] | Number of missiles of each type ordered 3, 1, 2
		fuel | int | Fuel state in 100s of lbs
		mission | str ('BAI', 'CAP', 'Strike', 'SEAD') | Mission type
	"""
	def __init__(self, mission_type_arg: str):
		super().__init__()

		# Easy bits
		plane_config = choice(planes)
		self.name = plane_config['name']
		self.callsign = choice(friendlies)
		self.guns = choices(['plus', 'minus'], weights=[.8, .2])[0]
		self.mission = mission_type_arg

		# Makes a bearing read properly by pyttsx3
		self.readable_bearing = ' '.join(list('0' * (3 - len(str(self.bearing))) + str(self.bearing)))

		# Prep for loadout making
		self.foxs = [0, 0, 0]
		self.fuel = randint(int(plane_config['fuel_max'] / 2), plane_config['fuel_max'])

		# Creates a list of possiblities and corresponding types for each pylon
		possibilities = []
		for i in range(plane_config['pylon_count']):
			if plane_config['payload']['5'][i] and uniform(0, 1) <= ground_chance[mission_type_arg]:
				possibility = False
			else:
				possibility = []

				for payload_ind in range(4):
					if plane_config['payload'][str(payload_ind + 1)][i]:
						possibility.append((payload_ind, plane_config['payload'][str(payload_ind + 1)][i]))

			possibilities.append(possibility)

		# Overrides pylon if mission type requires
		if mission_type in plane_config['payload_overrides'][0]:
			possibilities[choice(plane_config['payload_overrides'][1])] = False

		# Choses possibilities and adds to related value
		for possibility in possibilities:
			if possibility:
				chosen_payload = choice(possibility)
				if chosen_payload[0] <= 2:
					self.foxs[chosen_payload[0]] += chosen_payload[1]
				else:
					self.fuel += plane_config['fuel_add']


class LockedList:
	"""
	A list with a built-in threading.Lock \n
	Value is held in .val
	"""
	def __init__(self, *args):
		self.lock = thread.Lock()
		self.val = list(args)

	def __add__(self, other):
		self.val += other

	def __len__(self):
		return len(self.val)


class LockedVal:
	"""
		A variable with a built-in threading.Lock \n
		Value is held in .val
		"""
	def __init__(self, val):
		self.lock = thread.Lock()
		self.val = val

	def __eq__(self, other):
		if self.val == other:
			return True
		else:
			return False


def braa_to_bulls(origin: BasicPlane, bearing: int, range_val) -> tuple[int, int]:
	"""Converts a BRAA from origin to bullseye"""
	x1 = cos(radians((90 - origin.bearing) % 360)) * origin.dist
	y1 = sin(radians((90 - origin.bearing) % 360)) * origin.dist
	x2 = cos(radians((90 - bearing) % 360)) * range_val
	y2 = sin(radians((90 - bearing) % 360)) * range_val
	x_net = x1 + x2
	y_net = y1 + y2
	range_out = round(sqrt(x_net ** 2 + y_net ** 2))
	bearing_out = round((90 - degrees(atan2(y_net, x_net))) % 360)
	return bearing_out, range_out


def draw_border(drawer) -> None:
	"""
	Draws a border around the canvas given a turtle.RawTurtle, used for debugging canvas size
	"""
	canv_size = [content.bbox(0, 1, 0, 2)[2+i] + [-5, -6][i] for i in range(2)]
	tl_coords = (-draw.screen.screensize()[0] // 2, draw.screen.screensize()[1] // 2)
	drawer.clear()
	drawer.penup()
	drawer.goto(tl_coords[0], tl_coords[1])
	drawer.pendown()
	drawer.goto(tl_coords[0], tl_coords[1] - canv_size[1])
	drawer.goto(tl_coords[0] + canv_size[0], tl_coords[1] - canv_size[1])
	drawer.goto(tl_coords[0] + canv_size[0], tl_coords[1])
	drawer.goto(tl_coords[0], tl_coords[1])
	drawer.penup()


def draw_radar(drawer) -> None:
	"""Given a list of enemy and ally objects, draw them on the gui with drawer"""
	# Disables redraw button to prevent overlap
	redraw.config(state='disabled')
	border_drawer.config(state='disabled')

	# Get locks
	with friendly_planes.lock:
		allies = friendly_planes.val
	with enemy_planes.lock:
		enemies = enemy_planes.val
	with threat.lock:
		if threat.val:
			sam = threat.val
		else:
			sam = False

	# Drawer attributes
	drawer.clear()
	canv_size = [content.bbox(0, 1, 0, 2)[2+i] + [-5, -6][i] for i in range(2)]
	tl_coords = (-draw.screen.screensize()[0] // 2, draw.screen.screensize()[1] // 2)

	# Process allies and enemies
	enemy_coords = [[0, 0]]
	for enemy in enemies:
		enemy_coords.append([enemy.dist * cos(radians(90-enemy.bearing)), enemy.dist * sin(radians(90-enemy.bearing))])
	ally_coords = []
	for plane in allies:
		ally_coords.append([plane.dist * cos(radians(90-plane.bearing)), plane.dist * sin(radians(90-plane.bearing))])
	if sam:
		sam_coords = [sam.bulls_range * cos(radians(90-sam.bulls_bearing)),
					  sam.bulls_range * sin(radians(90-sam.bulls_bearing))]
		all_coords = enemy_coords + ally_coords + [sam_coords]
	else:
		all_coords = enemy_coords + ally_coords
	x_range = [max([i[0] for i in all_coords]), min([i[0] for i in all_coords])]
	y_range = [max([i[1] for i in all_coords]), min([i[1] for i in all_coords])]

	# Caculate drawing offset & scale
	bulls_coords = [-sum(x_range) / 2, -sum(y_range) / 2]
	drawer.goto(bulls_coords[0], bulls_coords[1])
	greatest_scalor = max([(x_range[0] - x_range[1]) / canv_size[0], (y_range[0] - y_range[1]) / canv_size[1]])
	drawing_scalar = uniform(0.5, 0.9) / greatest_scalor
	center = [tl_coords[0] + canv_size[0] / 2, tl_coords[1] - canv_size[1] / 2]
	bulls_coords = [drawing_scalar * bulls_coords[i] + center[i] for i in range(len(bulls_coords))]

	# Draw on canvas
	drawer.penup()
	drawer.goto(bulls_coords[0], bulls_coords[1])
	drawer.setheading(0)
	drawer.pendown()
	drawer.dot(5)
	drawer.penup()
	drawer.sety(bulls_coords[1] - 10)
	drawer.pendown()
	drawer.circle(10, steps=6)
	drawer.penup()

	with threat.lock:
		if threat.val:
			sam = threat.val
		else:
			sam = False
	if sam:
		drawer.color('orange')
		drawer.goto(bulls_coords[0], bulls_coords[1])
		drawer.setheading(90 - sam.bulls_bearing)
		drawer.fd(sam.bulls_range * drawing_scalar)
		drawer.pendown()
		drawer.dot(5)
		drawer.write(sam.name, font=('Arial', 10, 'normal'))
		drawer.penup()
		drawer.setheading(270)
		drawer.fd(sam.fire_range * drawing_scalar)
		drawer.setheading(0)
		drawer.pendown()
		drawer.circle(sam.fire_range * drawing_scalar, steps=35)
		drawer.penup()

	i = 1
	drawer.color('red')
	for plane in enemies:
		drawer.goto(bulls_coords[0], bulls_coords[1])
		drawer.setheading(90 - plane.bearing)
		drawer.fd(plane.dist * drawing_scalar)
		drawer.pendown()
		drawer.dot(5)
		drawer.write(i, font=('Arial', 10, 'normal'))
		drawer.setheading(90 - plane.heading)
		drawer.forward(plane.speed * drawing_scalar)
		drawer.penup()
		i += 1

	drawer.color('blue')
	for plane in allies:
		drawer.goto(bulls_coords[0], bulls_coords[1])
		drawer.setheading(90 - plane.bearing)
		drawer.fd(plane.dist * drawing_scalar)
		drawer.pendown()
		drawer.dot(5)
		if type(plane) in [NamedPlane]:
			drawer.write(str(i) + f' - {plane.callsign.capitalize()}', font=('Arial', 10, 'normal'))
		else:
			drawer.write(i, font=('Arial', 10, 'normal'))
		drawer.setheading(90 - plane.heading)
		drawer.forward(plane.speed * drawing_scalar)
		drawer.penup()
		i += 1

	drawer.color('black')

	# Renables next problem
	redraw.config(state='active')
	border_drawer.config(state='active')


def generate_and_draw() -> None:
	"""Temp funtion to test drawing and give buttons functionality"""
	with friendly_planes.lock:
		friendly_planes.val = []
	with enemy_planes.lock:
		enemy_planes.val = []
	for _ in range(4):
		plane = BasicPlane()
		if uniform(0, 1) >= .5:
			with friendly_planes.lock:
				friendly_planes.val.append(plane)
		else:
			with enemy_planes.lock:
				enemy_planes.val.append(plane)
	refresh_draw.set()


def update_braa() -> None:
	with friendly_planes.lock:
		friendly = friendly_planes.val
	with enemy_planes.lock:
		enemies = enemy_planes.val
	with braas.lock:
		braa_list = braas.val
	combined_planes = enemies + friendly
	for row in bulls_table:
		for item in row:
			item.config(text='')
	for row in braa_table:
		for item in row:
			item.config(text='')
	for ind in range(len(combined_planes)):
		bulls_table[ind][0].config(text=combined_planes[ind].bearing)
		bulls_table[ind][1].config(text=combined_planes[ind].dist)
		bulls_table[ind][2].config(text=combined_planes[ind].altitude)
		bulls_table[ind][3].config(text=combined_planes[ind].heading)
	for ind in range(len(braa_list)):
		braa_table[ind][0].config(text=braa_list[ind].bearing)
		braa_table[ind][1].config(text=braa_list[ind].dist)
		braa_table[ind][2].config(text=braa_list[ind].altitude)
		braa_table[ind][3].config(text=aspect_shorthand[braa_list[ind].aspect])


def check_in_call() -> None:
	# Set up situation & answer
	mission = choice(mission_types)
	plane = LoadoutPlane(mission)
	with solution_plane.lock:
		solution_plane.val = plane
	other_planes = [BasicPlane() for _ in range(randint(0, 6))]
	if other_planes:		# Splits to avoid calling nonexistent index
		split = randint(0, len(other_planes))
		if uniform(0, 1) < .75:		# 25% chance to give plane not on scope, 75% chance for contact
			plane_on_screen.set()
			with friendly_planes.lock:
				friendlies = other_planes[0:split]
				friendlies.insert(randint(0, split), plane)
				friendly_planes.val = friendlies
		else:
			plane_on_screen.clear()
			with friendly_planes.lock:
				friendly_planes.val = other_planes[0:split]
		with enemy_planes.lock:
			enemy_planes.val = other_planes[split:]
	else:
		with friendly_planes.lock:
			friendly_planes.val = [plane]

	# Draw problem and tts
	with problem_state.lock:
		problem_state.val = 'in-progress'

	refresh_draw.set()
	phrase = f"""{alias}, {plane.callsign} {randint(1, 9)} 1; {single_dict[randint(1, 4)]} ship {plane.name} \
			checking in for {mission}; bullseye {plane.readable_bearing} , {plane.dist} ; {plane.foxs[0]} \
			{plane.foxs[1]} {plane.foxs[2]} {plane.guns}, {int(plane.fuel / 10)} decimal {plane.fuel % 10}"""
	trans_phrase = ' '.join([translate_dict[i] for i in phrase.split(' ')])
	speaker = mp.Process(target=tts_say, args=(trans_phrase,))
	speaker.start()
	speaker.join()

	with problem_state.lock:
		problem_state.val = 'sent'


def check_check_in_answers() -> None:
	"""
	Checks user answers for check_in problem against stored solution
	DO NOT THREAD - Uses tk
	"""
	successes = []
	criticals = []
	moderates = []
	with solution_plane.lock:
		solution = solution_plane.val

	if solution.callsign == name_box.get().lower().split(' ')[0]:
		successes.append(name_box_label)
	else:
		moderates.append(name_box_label)

	if solution.name == plane_type.get().lower():
		successes.append(plane_type_label)
	else:
		moderates.append(plane_type_label)

	if solution.mission == mission_type.get():
		successes.append(mission_type_label)
	else:
		criticals.append(mission_type_label)

	allowable_bullseyes = [[str(solution.readable_bearing).replace(' ', ''), str(solution.dist)],
						   [str(solution.bearing), str(solution.dist)]]

	if bullseye_usr.get().split('/') in allowable_bullseyes:
		successes.append(bullseye_label)
	else:
		criticals.append(bullseye_label)

	if [str(count) for count in solution.foxs] == foxs.get().split(' '):
		successes.append(foxs_label)
	else:
		criticals.append(foxs_label)

	if (solution.guns == 'plus') == ('selected' in guns_usr.state()):
		successes.append(guns_label)
	else:
		criticals.append(guns_label)

	try:
		if solution.fuel / 10 == float(fuel_state.get().replace(',', '.')):
			successes.append(fuel_state_label)
		else:
			criticals.append(fuel_state_label)
	except ValueError:
		criticals.append(fuel_state_label)

	usr_return = [i.strip(',').lower() for i in check_in_stt.get().split(' ')]
	try:
		if plane_on_screen.is_set():
			if usr_return[0:1] + usr_return[2:5] != [solution.callsign, alias, 'radar', 'contact']:
				criticals.append(check_in_stt_label)
			else:
				successes.append(check_in_stt_label)
		else:
			if usr_return[0:1] + usr_return[2:] not in [[solution.callsign, alias, 'standby'],
								  [solution.callsign, alias, 'negative', 'contact']]:
				criticals.append(check_in_stt_label)
			else:
				successes.append(check_in_stt_label)
	except KeyError:
		criticals.append(check_in_stt_label)

	for label in successes:
		label.configure(fg='green')

	for label in criticals:
		label.configure(fg='red')

	for label in moderates:
		label.configure(fg='orange')


def threat_call() -> None:
	# Set up origin and solution
	origin_plane = NamedPlane(dist=randint(1, 40))
	solution_braa = BraaPlane(origin_plane)
	bullseye_solution = braa_to_bulls(origin_plane, solution_braa.bearing, solution_braa.dist)
	solution_enemy = BasicPlane(bullseye_solution[0], bullseye_solution[1], solution_braa.altitude, solution_braa.heading)
	friendlies = []
	enemy_braas = []
	enemy_bulls = []
	num_enemies = randint(0, 5)
	for ind in range(num_enemies):
		plane = BraaPlane(origin_plane, track=False, dist=randint(solution_braa.dist + 8, solution_braa.dist + 38))
		enemy_braas.append(plane)
		plane_bulls = braa_to_bulls(origin_plane, plane.bearing, plane.dist)
		enemy_bulls.append(BasicPlane(plane_bulls[0], plane_bulls[1], plane.altitude, plane.heading))
	for ind in range(randint(0, 5 - num_enemies)):
		plane = BraaPlane(origin_plane, track=False,
						  dist=randint(solution_braa.dist + 8, solution_braa.dist + 38), friendly= True)
		bulls_plane = braa_to_bulls(origin_plane, plane.bearing, plane.dist)
		friendlies.append(BasicPlane(bulls_plane[0], bulls_plane[1], plane.altitude, plane.heading))
	insert_pos_enemy = randint(0, len(enemy_braas))
	with braas.lock:
		enemy_braas.insert(insert_pos_enemy, solution_braa)
		braas.val = enemy_braas
	with solution_plane.lock:
		solution_plane.val = solution_braa
	with friendly_planes.lock:
		friendlies.insert(randint(0, len(friendlies)), origin_plane)
		friendly_planes.val = friendlies
	with enemy_planes.lock:
		enemy_bulls.insert(insert_pos_enemy, solution_enemy)
		enemy_planes.val = enemy_bulls

	refresh_draw.set()
	refresh_bulls.set()

	with problem_state.lock:
		problem_state.val = 'sent'


def threat_answers() -> None:
	"""
	Checks user answers for threat problem against stored solution
	DO NOT THREAD - Uses tk
	"""
	with solution_plane.lock:
		solution = solution_plane.val
	with friendly_planes.lock:
		origin = friendly_planes.val

	expected_phrases = [[origin[0].callsign, alias, 'threat', 'braa', str(solution.readable_bearing.replace(' ', '')),
						 str(solution.dist), str(solution.altitude), solution.aspect, 'track', *solution.cardinal.split(' ')],
						[origin[0].callsign, alias, 'threat', 'braa', str(solution.readable_bearing.replace(' ', '')),
						 str(solution.dist), str(solution.altitude), solution.aspect]]

	usr_phrase = [i.strip(',').lower() for i in text_entry.get().split(' ')]

	if usr_phrase[0:1] + usr_phrase[2:] in expected_phrases:
		stt_instructions.config(fg='green')
	else:
		stt_instructions.config(fg='red')


def caution_call() -> None:
	origin_plane = NamedPlane()
	sam = Threat(origin_plane)
	friendlies = []
	for i in range(randint(0,5)):
		plane = BraaPlane(origin_plane, track=False,
						  dist=randint((sam.dist + 8) // 1, (sam.dist + 50) // 1), friendly=True)
		bulls_plane = braa_to_bulls(origin_plane, plane.bearing, plane.dist)
		friendlies.append(BasicPlane(bulls_plane[0], bulls_plane[1], plane.altitude, plane.heading))

	with solution_plane.lock:
		solution_plane.val = origin_plane
	with braas.lock:
		braas.val = [sam]
	with friendly_planes.lock:
		friendlies.insert(randint(0, len(friendlies)), origin_plane)
		friendly_planes.val = friendlies
	with threat.lock:
		threat.val = sam

	refresh_draw.set()
	refresh_bulls.set()

	with problem_state.lock:
		problem_state.val = 'sent'


def caution_answers() -> None:
	"""
	Checks user answers for caution problem against stored solution
	DO NOT THREAD - Uses tk
	"""
	with solution_plane.lock:
		friendly = solution_plane.val
	with threat.lock:
		sam = threat.val

	expected_phrases = [[friendly.callsign, alias, 'caution', sam.name, sam.readable_bearing + '/' + str(sam.bulls_range)],
						[friendly.callsign, alias, 'caution', sam.sign, sam.readable_bearing + '/' + str(sam.bulls_range)]]

	usr_in = [i.strip(',').lower() for i in text_entry.get().split(' ')]

	if (usr_in[0:1] + usr_in[2:]) in expected_phrases:
		stt_instructions.config(fg='green')
	else:
		stt_instructions.config(fg='red')


# Window building and main loop
if __name__ == '__main__':
	root = tk.Tk()
	root.title('GCI Trainer')
	root.geometry('850x500')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)

	content = ttk.Frame(root)
	content.grid(column=0, row=0, sticky='NSEW')
	content.columnconfigure(0, weight=4, minsize=200)
	content.columnconfigure(1, weight=1, minsize=200)
	content.rowconfigure(0, weight=0, minsize=25)
	content.rowconfigure(1, weight=1, minsize=100)
	content.rowconfigure(2, weight=1, minsize=25)
	content.rowconfigure(3, weight=0, minsize=100)

	# Window management button overrides
	root.protocol("WM_DELETE_WINDOW", root.destroy)


	# Infobar bits
	infobar = ttk.Frame(content)
	infobar.grid(column=0, row=0, sticky='NSWE')
	infobar.columnconfigure(0, weight=0)
	infobar.columnconfigure(1, weight=0)
	infobar.columnconfigure(2, weight=1)
	infobar.columnconfigure(3, weight=0)

	ttk.Label(infobar, text='GCI Trainer').grid(column=2, padx='25', row=0, sticky='NS')
	ttk.Label(infobar, text='V0.3.0-alpha').grid(column=3, row=0, sticky='E')


	# Main display
	display = tk.Canvas(content)
	display.grid(column=0, row=1, rowspan=2, sticky='NSEW')
	draw = turtle.RawTurtle(display)
	draw.speed(0)
	draw.hideturtle()
	draw.penup()

	border_drawer = ttk.Button(infobar, text='Draw frame', command=lambda: draw_border(draw))
	border_drawer.grid(column=0, row=0, sticky='WE')

	canvas_tester = ttk.Button(infobar, text='Draw radar', command=lambda: generate_and_draw())
	canvas_tester.grid(column=1, row=0, sticky='WE')


	# Settings
	settings = ttk.Frame(content, borderwidth=4, relief='ridge')
	settings.grid(column=1, row=0, rowspan=2, sticky='NSEW')
	settings.columnconfigure(0, weight=1, minsize=70)
	settings.columnconfigure(1, weight=1)
	settings.columnconfigure(2, weight=0)
	settings.rowconfigure(0, weight=0, minsize=10)
	settings.rowconfigure(1, weight=1)
	settings.rowconfigure(2, weight=1)
	settings.rowconfigure(3, weight=1)
	settings.rowconfigure(4, weight=0, minsize=10)

	problem_label = ttk.Label(settings, text='Please select a problem type')
	problem_label.grid(column=0, columnspan=2, row=0, sticky='NSW')

	check_in = ttk.Checkbutton(settings, text='Check-in')
	check_in.grid(column=0, columnspan=2, row=1, sticky='NSW')
	check_in.state(['!alternate'])

	bogey_dope = ttk.Checkbutton(settings, text='Threat')
	bogey_dope.grid(column=0, columnspan=2, row=2, sticky='NSW')
	bogey_dope.state(['!alternate'])

	caution = ttk.Checkbutton(settings, text='Caution')
	caution.grid(column=0, columnspan=2, row=3, sticky='NSW')
	caution.state(['!alternate'])

	wpm_label = ttk.Label(settings, text='TTS WPM')
	wpm_label.grid(column=0, row=4, sticky='NSEW')
	wpm = ttk.Spinbox(settings, from_=150, to=300, increment=10, command=lambda: tts_set_speed(int(wpm.get())))
	wpm.set(200)
	wpm.grid(column=1, row=4, sticky='NSEW')

	set_scroll = ttk.Scrollbar(settings, orient='vertical')
	set_scroll.grid(column=2, row=0, rowspan=2, sticky='NSE')

	problem_boxes = [check_in, bogey_dope, caution]


	# BRAA/Bullseyes & problem management
	bulls = ttk.Frame(content, borderwidth=4, relief='ridge')
	bulls.grid(column=1, row=2, rowspan=2, sticky='NSEW')
	bulls.columnconfigure(0, weight=1)
	bulls.columnconfigure(1, weight=1)
	bulls.columnconfigure(2, weight=1)
	bulls.rowconfigure(0, weight=1)
	bulls.rowconfigure(1, weight=0, minsize=25)

	# BRAA/Bullseye pages
	bulls_notebook = ttk.Notebook(bulls)
	braa_page = ttk.Frame(bulls_notebook)
	bulls_page = ttk.Frame(bulls_notebook)
	bulls_notebook.add(braa_page, text='BRAA')
	bulls_notebook.add(bulls_page, text='Bullseye')
	bulls_notebook.grid(column=0, columnspan=3, row=0, sticky='NSEW')

	# BRAA table
	braa_page.columnconfigure(0, weight=3)
	braa_page.columnconfigure(1, weight=2)
	braa_page.columnconfigure(2, weight=2)
	braa_page.columnconfigure(3, weight=3)
	braa_page.rowconfigure(0, weight=0)
	for i in range(7):
		braa_page.rowconfigure(i + 1, weight=1)
	ttk.Label(braa_page, text='Bearing').grid(column=0, row=0)
	ttk.Label(braa_page, text='Range').grid(column=1, row=0)
	ttk.Label(braa_page, text='Altitude').grid(column=2, row=0)
	ttk.Label(braa_page, text='Aspect').grid(column=3, row=0)
	braa_table = [[ttk.Label(braa_page) for __ in range(4)] for _ in range(7)]
	for ind in range(len(braa_table)):
		for jnd in range(len(braa_table[0])):
			braa_table[ind][jnd].grid(column=jnd, row=ind + 1)

	# Bulls table
	bulls_page.columnconfigure(0, weight=3)
	bulls_page.columnconfigure(1, weight=2)
	bulls_page.columnconfigure(2, weight=2)
	bulls_page.columnconfigure(3, weight=3)
	bulls_page.rowconfigure(0, weight=0)
	for i in range(7):
		bulls_page.rowconfigure(i + 1, weight=1)
	ttk.Label(bulls_page, text='Bearing').grid(column=0, row=0)
	ttk.Label(bulls_page, text='Range').grid(column=1, row=0)
	ttk.Label(bulls_page, text='Altitude').grid(column=2, row=0)
	ttk.Label(bulls_page, text='Heading').grid(column=3, row=0)
	bulls_table = [[ttk.Label(bulls_page) for __ in range(4)] for _ in range(7)]
	for ind in range(len(bulls_table)):
		for jnd in range(len(bulls_table[0])):
			bulls_table[ind][jnd].grid(column=jnd, row=ind + 1)

	# Problem management buttons
	submit = ttk.Button(bulls, text='Submit', command=lambda: submit_answers.set())
	submit.grid(column=0, row=1, sticky='NSEW')

	redraw = ttk.Button(bulls, text='Redraw', command=lambda: refresh_draw.set())
	redraw.grid(column=1, row=1, sticky='NSEW')

	nextproblem = ttk.Button(bulls, text="New", command=lambda: new_problem.set())
	nextproblem.grid(column=2, row=1, sticky='NSEW')


	# Answers
	answers = ttk.Frame(content)
	answers.grid(column=0, row=3, sticky='NSEW')
	answers.columnconfigure(0, weight=1)
	answers.rowconfigure(0, weight=1)

	answer_notebook = ttk.Notebook(answers)

	stt_answers = ttk.Frame(answer_notebook)
	stt_answers.columnconfigure(0, weight=1)
	stt_answers.rowconfigure(0, weight=1)
	stt_answers.rowconfigure(1, weight=1)

	text_entry = DefaultEntryBox('Enter call here or use text to speech', stt_answers, default_justify='left')
	text_entry.grid(column=0, row=0, sticky='NSEW', padx=5, pady=5)
	# noinspection PyUnboundLocalVariable
	stt_instructions = tk.Label(stt_answers, text=f'For speech to text press {stt_key}')
	stt_instructions.grid(column=0, row=1, sticky='W', padx=5, pady=5)

	check_in_answers = ttk.Frame(answer_notebook)
	check_in_answers.rowconfigure(0, weight=1)
	check_in_answers.rowconfigure(1, weight=1)
	check_in_answers.rowconfigure(2, weight=1)
	for i in range(7):
		check_in_answers.columnconfigure(i, weight=1, minsize=80)

	name_box_label = tk.Label(check_in_answers, text='Flight name')
	name_box_label.grid(column=0, row=0)
	name_box = DefaultEntryBox('Callsign X-X', check_in_answers)
	name_box.grid(column=0, row=1)
	plane_type_label = tk.Label(check_in_answers, text='Plane type')
	plane_type_label.grid(column=1, row=0)
	plane_type = ttk.Combobox(check_in_answers)
	plane_type['values'] = ('F-16', 'F-18', 'JF-17')
	plane_type.grid(column=1, row=1)
	mission_type_label = tk.Label(check_in_answers, text='Mission type')
	mission_type_label.grid(column=2, row=0)
	mission_type = ttk.Combobox(check_in_answers)
	mission_type['values'] = ('CAP', 'BAI', 'SEAD', 'Strike')
	mission_type.grid(column=2, row=1)
	bullseye_label = tk.Label(check_in_answers, text='Alpha check')
	bullseye_label.grid(column=3, row=0)
	bullseye_usr = DefaultEntryBox('BBB/RR', check_in_answers)
	bullseye_usr.grid(column=3, row=1)
	foxs_label = tk.Label(check_in_answers, text='Missile count')
	foxs_label.grid(column=4, row=0)
	foxs = DefaultEntryBox('X X X', check_in_answers)
	foxs.grid(column=4, row=1)
	guns_label = tk.Label(check_in_answers, text='Guns')
	guns_label.grid(column=5, row=0)
	guns_usr = ttk.Checkbutton(check_in_answers)
	guns_usr.grid(column=5, row=1)
	guns_usr.state(['!alternate'])
	fuel_state_label = tk.Label(check_in_answers, text='Fuel state')
	fuel_state_label.grid(column=6, row=0)
	fuel_state = DefaultEntryBox('XX.X', check_in_answers)
	fuel_state.grid(column=6, row=1)
	check_in_stt = DefaultEntryBox('Enter response here or use text to speech', check_in_answers, default_justify='left')
	check_in_stt.grid(column=0, columnspan=5, row=2, sticky='NSEW')
	check_in_stt_label = tk.Label(check_in_answers, text=f'For text to speech press {stt_key}')
	check_in_stt_label.grid(column=5, columnspan=2, row=2, sticky='NSEW', padx=2)
	check_in_labels = [stt_instructions, name_box_label, plane_type_label, mission_type_label, bullseye_label,
					   foxs_label, guns_label, fuel_state_label, check_in_stt_label]

	answer_boxes = [text_entry, name_box, plane_type, mission_type, bullseye_usr, foxs, fuel_state, check_in_stt]
	default_boxes = [text_entry, name_box, bullseye_usr, foxs, fuel_state, check_in_stt]
	answer_notebook.add(stt_answers, text='General')
	answer_notebook.add(check_in_answers, text='Check-in')
	answer_notebook.grid(column=0, row=0, sticky='NSEW', padx=2, pady=2)


	# Setup environment thread variables
	refresh_bulls = thread.Event()
	refresh_draw = thread.Event()
	new_problem = thread.Event()
	plane_on_screen = thread.Event()
	submit_answers = thread.Event()
	stt_state = LockedVal('none')
	problem_state = LockedVal('none')
	solution_plane = LockedVal(BasicPlane())
	threat = LockedVal(None)
	braas = LockedList([])
	friendly_planes = LockedList([BasicPlane()])
	enemy_planes = LockedList([BasicPlane()])
	problem_choice = 'none'

	problem_dict = {
		'Check-in': check_in_call,
		'Threat': threat_call,
		'Caution': caution_call
	}

	answer_dict = {
		check_in_call: lambda: answer_notebook.select(1),
		threat_call: lambda: answer_notebook.select(0),
		caution_call: lambda: answer_notebook.select(0)
	}


	# Main loop
	while True:
		try:
			root.state()
		except tk.TclError:
			break

		problems = []
		for box in problem_boxes:
			if 'selected' in box.state():
				problems.append(box.cget('text'))

		if problems:
			problem_label.config(text='All good!')
		else:
			problem_label.config(text='Please select a problem type')
			new_problem.clear()

		if new_problem.is_set():
			with problem_state.lock:
				if problem_state != 'in-progress':
					# Reset vars
					with threat.lock:
						threat.val = None
					with braas.lock:
						braas.val = []
					with enemy_planes.lock:
						enemy_planes.val = []
					with friendly_planes.lock:
						friendly_planes.val = []
					# Reset answers
					for label in check_in_labels:
						label.config(fg='black')
					for box in answer_boxes:
						box.delete(0, 'end')
					guns_usr.state(['!selected'])
					# Setup problem
					problem_choice = problem_dict[choice(problems)]
					answer_dict[problem_choice]()
					for box in default_boxes:
						box.prompt()
					problem = thread.Thread(target=problem_choice)
					problem_state.val = 'inited'
					problem.start()
					problem_label.config(text='All good!')
					new_problem.clear()
				else:
					# Update error
					problem_label.config(text='Waiting for text to speech to join')

		# Prevent manual entry if stt is enabled
		with stt_state.lock:
			if stt_state.val == 'disable':
				text_entry.configure(state='disabled')
				check_in_stt.configure(state='disabled')
				stt_state.val = 'none'
			elif stt_state.val == 'enable':
				text_entry.configure(state='normal')
				check_in_stt.configure(state='normal')
				stt_state.val = 'none'

		if submit_answers.is_set():
			if problem_choice == check_in_call:
				check_check_in_answers()
			elif problem_choice == threat_call:
				threat_answers()
			elif problem_choice == caution_call:
				caution_answers()
			submit_answers.clear()

		# Update turtle
		if refresh_draw.is_set():
			draw_radar(draw)
			refresh_draw.clear()

		if refresh_bulls.is_set():
			update_braa()
			refresh_bulls.clear()

		root.update_idletasks()
		root.update()

	try:
		if problem.is_alive():
			print('Preventing zombie threads...')
			problem.join()
			print('Done!')
	except NameError:
		pass
