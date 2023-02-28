from GCI_structures import Braa, Bulls, LockVal, Response, TranslateDict
from math import asin, atan2, cos, degrees, radians, sin, sqrt
from multiprocessing import Process
from random import choice, choices, randint, uniform
from tkinter import ttk
from typing import Literal
import tkinter as tk
import tomllib as tom
import threading
import tk_objects
import tts


class Plane:
	"""
		Creates a plane with name, number, bullseye, and optional braa
		Parameters:
			gen_mode | Mode of position genertion
			info_text | Configures if the plane has a displayed name and number
			bullseye | Bulls object of plane, used for reference in a braa genertion
			target | Braa object of a target plane, used for reference in a braa generation
		Properties:
			sign | Callsign of plane
			num | Flight number of plane
			text | Extra text to be displayed on radar screen
			bulls | Bulls object containing position of plane
			braa | Braa object containing position of plane relative to bullseye parameter
			speed | Speed of plane in nm/30 sec, multiply by 120 for knots
	"""
	def __init__(self, gen_mode: Literal['random', 'f_braa', 'h_braa', 't_braa'] = 'random',
				 info_text: bool = True, bullseye: Bulls = None, target: Braa = None):
		self.sign = avail_signs.pop(randint(0, len(avail_signs) - 1))
		self.num = randint(1, 4)
		if info_text and gen_mode in ['random', 'f_braa']:
			self.text = f'{self.sign.capitalize()} {self.num}'
		else:
			self.text = ''

		# Braa modes are repetitive, only first is commented
		if gen_mode == 'random':			# If looking for random plane (check-in)
			if bullseye is None:
				self.bulls = Bulls(randint(0, 359), randint(2, 95), randint(1, 40), randint(0, 359))
			else:
				self.bulls = bullseye
			self.braa = Braa('N/A', 'N/A', 'N/A', 'N/A', None, 'N/A')
		elif gen_mode == 't_braa':			# If looking for target plane in a braa situation
			rough_bearing_r = randint(bullseye.heading - 75, bullseye.heading + 75)			# Gets a rough bearing
			bearing_r = rough_bearing_r % 360							# Rounds out rough bearing to [0, 359]
			bearing_rel_h = rough_bearing_r - bullseye.heading			# Gets the bearing relative to the heading of the origin
			# Bearing magic to get heading roughly on intercept relative to origin heading
			heading_rel_h = randint(int((1.3 * bearing_rel_h - 202.5) // 1), int((1.3 * bearing_rel_h - 157.5) // 1))
			heading = (heading_rel_h + bullseye.heading) % 360			# Translates to world heading and rounds out
			# Gets aspect as a string using relative heading (aspect magic)
			asp = abs((bearing_rel_h - 180) - heading_rel_h)
			asp_str = aspect_translate[abs(((180 - asp) % 360 - 180) // 30 + 0.5)]
			# Gets cardinal direction as a string using heading (heading less-magic)
			cardinal_str = cardinal_translate[((heading + 22.5) // 45) % 8]
			self.braa = Braa(bearing_r, randint(5, 30), randint(1, 40), heading, asp_str, cardinal_str)
			self.bulls = braa_to_bulls(bullseye, self.braa)
		elif gen_mode == 'h_braa':			# If looking for hostile plane in a braa situation
			rough_bearing_r = randint(bullseye.heading - 75, bullseye.heading + 75)
			bearing_r = rough_bearing_r % 360
			bearing_rel_h = rough_bearing_r - bullseye.heading
			heading = randint(0, 359)
			asp = abs((bearing_rel_h - 180) - (heading - bullseye.heading))		# Gets integer aspect of target
			asp_str = aspect_translate[abs(((180 - asp) % 360 - 180) // 30 + 0.5)]		# Translates interger aspect to string
			cardinal_str = cardinal_translate[((heading + 22.5) // 45) % 8]
			self.braa = Braa(bearing_r, randint(target.dist + 8, target.dist + 40), randint(10, 40), heading, asp_str, cardinal_str)
			self.bulls = braa_to_bulls(bullseye, self.braa)
		elif gen_mode == 'f_braa':			# If looking for friendly plane in a braa situation
			rough_bearing_r = randint(bullseye.heading - 225, bullseye.heading - 105)
			bearing_r = rough_bearing_r % 360
			bearing_rel_h = rough_bearing_r - bullseye.heading
			heading = randint(0, 359)
			asp = abs((bearing_rel_h - 180) - (heading - bullseye.heading))		# Gets integer aspect of targe
			asp_str = aspect_translate[abs(((180 - asp) % 360 - 180) // 30 + 0.5)]		# Translates interger aspect to string
			cardinal_str = cardinal_translate[((heading + 22.5) // 45) % 8]
			self.braa = Braa(bearing_r, randint(15, 50), randint(10, 40), heading, asp_str, cardinal_str)
			self.bulls = braa_to_bulls(bullseye, self.braa)

		self.speed = round(uniform(2, 10), 1)


class LoadoutPlane(Plane):
	def __init__(self):
		super().__init__(info_text=False)
		model = choice(planes)
		self.name = model['name']
		self.guns = choices(['plus', 'minus'], weights=[.8, .2])[0]
		guns_bool = self.guns == 'plus'
		self.mission = choice(mission_types)
		self.foxs = [0, 0, 0]
		self.fuel = randint(int(model['fuel_max'] / 2), model['fuel_max'])

		# Pylon time
		possibilities = []
		for i in range(model['pylon_count']):
			if model['payload']['5'][i] and uniform(0, 1) <= ground_chance[self.mission]:
				possibility = False
			else:
				possibility = []

				for payload_ind in range(4):
					if model['payload'][str(payload_ind + 1)][i]:
						possibility.append((payload_ind, model['payload'][str(payload_ind + 1)][i]))

			possibilities.append(possibility)

		# Overrides pylon if mission type requires
		if self.mission in model['payload_overrides'][0]:
			possibilities[choice(model['payload_overrides'][1])] = False

		# Choses possibilities and adds to related value
		for possibility in possibilities:
			if possibility:
				chosen_payload = choice(possibility)
				if chosen_payload[0] <= 2:
					self.foxs[chosen_payload[0]] += chosen_payload[1]
				else:
					self.fuel += model['fuel_add']

		self.answers = [self.sign + ' ' + str(self.num) + '-1', self.name, self.mission,
						self.bulls.readable + '/' + str(self.bulls.dist), ' '.join([str(fox) for fox in self.foxs]),
						guns_bool, str(self.fuel / 10)]


class Sam:
	def __init__(self, bullseye: Bulls):
		model = choice(sam_types)
		self.text = model['name']
		self.name = self.text.lower()
		self.sign = model['shorthand']
		self.fire_range = model['range']
		if self.fire_range >= 10:
			self.fire_range *= 0.8

		dist = round(uniform(self.fire_range, self.fire_range + 4))
		# Gets a bearing deviation from bullseye within fire_range
		# Not entirely sure why I need to clamp here, but it sometimes throws a domain error
		bearing_off = degrees(asin(max(-1, min(1, self.fire_range / dist)))) * 0.85 // 1
		rough_bearing = randint(bullseye.heading - bearing_off, bullseye.heading + bearing_off)
		bearing_r = rough_bearing % 360
		self.braa = Braa(bearing_r, dist, 'N/A', 'N/A', None, None)
		self.bulls = braa_to_bulls(bullseye, self.braa)


class Window(ttk.Frame):
	def __init__(self,  *args, **kwargs):
		super().__init__(*args, **kwargs)					# Init frame
		self.grid(column=0, row=0, sticky='NSEW')			# Grid out self
		self.columnconfigure(0, weight=1, minsize=200)		# Configure columns
		self.columnconfigure(1, weight=0, minsize=200)
		self.rowconfigure(0, weight=0, minsize=25)			# Configure rows
		self.rowconfigure(1, weight=1, minsize=100)
		self.rowconfigure(2, weight=1, minsize=25)
		self.rowconfigure(3, weight=0, minsize=100)

		# Infobar
		self.infobar = tk_objects.InfoBar('v0.4.0-alpha', self)
		self.infobar.grid(column=0, row=0, sticky='NSEW', padx=5)

		# Problem management
		self.prob_man = tk_objects.ProblemManagement(lambda: check_answer.set(), lambda: new_problem.set(),
													 self.draw_radar, self, borderwidth=4, relief='ridge')
		self.prob_man.grid(column=1, row=2, rowspan=2, sticky='NSEW')

		# Canvas
		self.radar = tk_objects.RadarScreen(self)
		self.radar.grid(column=0, row=1, rowspan=2, sticky='NSEW')

		# Settings
		self.settings = tk_objects.SettingsBox(tts.tts_set_speed, self, borderwidth=4, relief='ridge')
		self.settings.grid(column=1, row=0, rowspan=2, sticky='NSEW')
		self.settings.set_funcs(check_in, threat, caution, lambda: self.status_write('Select a problem type'))

		# Answer bar
		self.answers = tk_objects.AnswerBox(sr_key, self)
		self.answers.grid(column=0, row=3, sticky='NSEW')

		# Vars
		self.canv_affectors = (self.prob_man.button_r, self.prob_man.button_m)

	def _disable_canv_affectors(self):
		for button in self.canv_affectors:
			button.config(state='disabled')
		self.radar.drawing = True
		self.radar.ruler_down = False

	def _enable_canv_affectors(self):
		for button in self.canv_affectors:
			button.config(state='active')
		self.radar.drawing = False

	def draw_radar(self):
		self.radar.set_planes(friend_list.val, hostile_list.val, threat_list.val)
		self.radar.set_scalar()
		self._disable_canv_affectors()
		self.radar.draw.clear()
		self.radar.draw.setheading(0)
		self.radar.draw_bulls()
		self.radar.draw_planes()
		self._enable_canv_affectors()

	def get_answers(self):
		if problem_func == caution:
			usr = self.answers.gen_answers
			return Response(usr, r'\w+ \d-\d \w+ caution \S+ (bullseye \d{3}( for | |/)\d+|braa \d{3} \d+)')
		elif problem_func == threat:
			usr = self.answers.gen_answers
			return Response(usr, r'\w+ \d-\d \w+ threat (bullseye \d{3}( for |/| )\d+ (at )?\d+ thousand track \w+ hostile|braa \d{3} \d+ \d+ thousand \w+( \w+)? hostile)')
		elif problem_func == check_in:
			usr = self.answers.check_answers
			usr[-1] = Response(usr[-1], r'\w+ \d-\d \w+ (standby|(radar|negative) contact)')
			return usr

	def reset_answers(self):
		self.answers.reset_colors()
		for box in self.answers.answer_boxes:
			try:
				box.prompt()
			except AttributeError:
				box.delete(0, 'end')

	def remove_corrections(self):
		for label in self.prob_man.error_labels:
			label.grid_remove()

	def set_check_color(self, inds):
		for i in range(len(self.answers.labels[:-1])):
			if i in inds:
				self.answers.labels[i].config(fg='green')
			else:
				self.answers.labels[i].config(fg='red')

	def set_gen_color(self, color):
		self.answers.gen_text.config(fg=color)

	def status_write(self, msg: str):
		self.infobar.status.config(text=msg)


def do_nothing() -> None:
	pass


def braa_to_bulls(origin: Bulls, target: Braa) -> Bulls:
	"""
		Converts a BRAA from origin to bullseye
		Could probably be done with law of cosines, but I can't be bothered to figure out the angle rounding
	"""
	x1 = cos(radians((90 - origin.bearing) % 360)) * origin.dist
	y1 = sin(radians((90 - origin.bearing) % 360)) * origin.dist
	x2 = cos(radians((90 - target.bearing) % 360)) * target.dist
	y2 = sin(radians((90 - target.bearing) % 360)) * target.dist
	x_net = x1 + x2
	y_net = y1 + y2
	range_out = round(sqrt(x_net ** 2 + y_net ** 2))
	bearing_out = round((90 - degrees(atan2(y_net, x_net))) % 360)
	return Bulls(bearing_out, range_out, target.altitude, target.heading)


def caution() -> None:
	sol_plane = Plane()
	sol_sam = Sam(sol_plane.bulls)

	enemies = []
	friendlies = []
	other_count = randint(0, 6)
	split = randint(0, other_count)
	for i in range(0, split):
		friendlies.append(Plane('f_braa', bullseye=sol_plane.bulls))
	for i in range(split, other_count):
		enemies.append(Plane('h_braa', bullseye=sol_plane.bulls, target=sol_sam.braa))
	friendlies.insert(randint(0, len(friendlies)), sol_plane)

	friend_list.val = friendlies
	hostile_list.val = enemies
	threat_list.val = [sol_sam]
	solution_vals.val = (sol_plane, sol_sam)
	draw_radar.set()


def caution_answers() -> None:
	usr_ans = app.get_answers()
	sol_vals = solution_vals.val
	sol_plane = sol_vals[0]
	sol_sam = sol_vals[1]

	errors = []
	if not usr_ans.sign:
		errors.append('no_addr')
	else:
		if (usr_ans.sign, usr_ans.num) != (sol_plane.sign, sol_plane.num):
			errors.append('call_id')
		if usr_ans.alias != alias:
			errors.append('self_id')
	if usr_ans.sam_type not in [sol_sam.name.lower(), sol_sam.sign]:
		errors.append('sam_type')
	if usr_ans.braa:
		errors.append('bad_braa')
		if abs(usr_ans.braa.bearing - sol_sam.braa.bearing) > 3:
			errors.append('bearing')
		if abs(usr_ans.braa.dist - sol_sam.braa.dist) > 1:
			errors.append('dist')
	elif usr_ans.braa:
		if abs(usr_ans.bulls.bearing - sol_sam.bulls.bearing) > 3:
			errors.append('bearing')
		if abs(usr_ans.bulls.dist - sol_sam.bulls.dist) > 1:
			errors.append('dist')
	else:
		errors.append('no_loc')
	if not usr_ans.form:
		errors.append('caut_form')

	app.prob_man.write_errors(errors)

	if errors:
		app.set_gen_color('red')
	else:
		app.set_gen_color('green')


def check_in() -> None:
	sol_plane = LoadoutPlane()

	phrase = f"""
		{alias}, {sol_plane.sign} {trans_dict[sol_plane.num]} 1; {single_dict[randint(1, 4)]} ship {sol_plane.name} checking \
		in for {sol_plane.mission}; bullseye {' '.join([i for i in sol_plane.bulls.readable])} for {sol_plane.bulls.dist}; \
		{sol_plane.foxs[0]} {sol_plane.foxs[1]} {sol_plane.foxs[2]}, {sol_plane.guns}, {sol_plane.fuel // 10} decimal \
		{sol_plane.fuel % 10}
		"""
	process = Process(target=tts.tts_say, args=(phrase,))
	process.start()

	enemies = []
	friendlies = []
	other_count = randint(1, 6)
	split = randint(1, other_count)
	for i in range(0, split):
		friendlies.append(Plane(info_text=False))
	for i in range(split, other_count):
		enemies.append(Plane(info_text=False))

	if uniform(0, 1) >= 0.75:
		on_screen = False
	else:
		friendlies.insert(randint(0, len(friendlies)), sol_plane)
		on_screen = True

	friend_list.val = friendlies
	hostile_list.val = enemies
	solution_vals.val = (sol_plane, on_screen)
	draw_radar.set()

	process.join()


def check_in_answers() -> None:
	sol_vals = solution_vals.val
	sol_plane = sol_vals[0]
	on_screen = sol_vals[1]
	usr_answers = app.get_answers()
	usr_ans = usr_answers[-1]

	errors = []
	sucesses = []
	for (ans, usr) in zip(sol_plane.answers, usr_answers[:-1]):
		try:
			if usr.lower() == ans.lower():
				sucesses.append(usr_answers.index(usr))
		except AttributeError:
			if usr == ans:
				sucesses.append(usr_answers.index(usr))

	if not usr_ans.sign:
		errors.append('no_addr')
	else:
		if (usr_ans.sign, usr_ans.num) != (sol_plane.sign, sol_plane.num):
			errors.append('call_id')
		if usr_ans.alias != alias:
			errors.append('self_id')
	if usr_ans.contact != on_screen:
		errors.append('contact')
	if not usr_ans.form:
		errors.append('chk_form')
	if not errors:
		sucesses.append(len(usr_answers) - 1)

	app.prob_man.write_errors(errors)

	app.set_check_color(sucesses)


def threat() -> None:
	sol_plane = Plane()
	sol_enemy = Plane('t_braa', bullseye=sol_plane.bulls)

	enemies = []
	friendlies = []
	other_count = randint(0, 6)
	split = randint(0, other_count)
	for i in range(0, split):
		friendlies.append(Plane('f_braa', bullseye=sol_plane.bulls))
	for i in range(split, other_count):
		enemies.append(Plane('h_braa', bullseye=sol_plane.bulls, target=sol_enemy.braa))
	friendlies.insert(randint(0, len(friendlies)), sol_plane)
	enemies.insert(randint(0, len(enemies)), sol_enemy)

	friend_list.val = friendlies
	hostile_list.val = enemies
	solution_vals.val = (sol_plane, sol_enemy)
	draw_radar.set()


def threat_answers() -> None:
	usr_ans = app.get_answers()
	sol_vals = solution_vals.val
	sol_origin = sol_vals[0]
	sol_enemy = sol_vals[1]

	errors = []
	if not usr_ans.sign:
		errors.append('no_addr')
	else:
		if (usr_ans.sign, usr_ans.num) != (sol_origin.sign, sol_origin.num):
			errors.append('call_id')
		if usr_ans.alias != alias:
			errors.append('self_id')
	if usr_ans.braa:
		if abs(usr_ans.braa.bearing - sol_enemy.braa.bearing) > 3:
			errors.append('bearing')
		if abs(usr_ans.braa.dist - sol_enemy.braa.dist) > 1:
			errors.append('dist')
		if usr_ans.braa.altitude != sol_enemy.braa.altitude:
			errors.append('altitude')
		if usr_ans.braa.aspect != sol_enemy.braa.aspect:
			errors.append('aspect')
		if usr_ans.braa.cardinal:
			if usr_ans.braa.cardinal != sol_enemy.braa.cardinal:
				errors.append('cardinal')
	if usr_ans.bulls:
		errors.append('bad_bulls')
	else:
		errors.append('no_loc')
	if not usr_ans.form:
		errors.append('thr_form')

	app.prob_man.write_errors(errors)

	if errors:
		app.set_gen_color('red')
	else:
		app.set_gen_color('green')



def clear_vals() -> None:
	"""
		Clears per-problem locked variables
	"""
	friend_list.val = []
	hostile_list.val = []
	threat_list.val = []
	solution_vals.val = []
	global avail_signs
	avail_signs = list(callsigns)


def test_draw() -> None:
	"""
		Draws a random radar screen
	"""
	enemies = []
	friendlies = []
	for _ in range(randint(1, 7)):
		choice([enemies, friendlies]).append(Plane())
	friend_list.val = friendlies
	hostile_list.val = enemies
	app.draw_radar()
	global avail_signs
	avail_signs = list(callsigns)


if __name__ == '__main__':
	# Constant variables and useful dictionaries
	mission_types = ['CAP', 'BAI', 'Strike', 'SEAD']
	single_dict = {1: 'single', 2: 2, 3: 3, 4: 4}
	trans_dict = TranslateDict()
	trans_dict[9] = 'niner'
	aspect_translate = {0.5: 'hot', 1.5: 'flanking', 2.5: 'beaming', 3.5: 'beaming', 4.5: 'drag', 5.5: 'drag'}
	cardinal_translate = {0: 'north', 1: 'northeast', 2: 'east', 3: 'southeast',
						  4: 'south', 5: 'southwest', 6: 'west', 7: 'northwest'}

	# Read configs
	with open('callsigns.txt', 'r') as file:
		callsigns = file.read().split(', ')
		avail_signs = list(callsigns)

	with open('config.toml', 'rb') as file:
		config_dict = tom.load(file)

	# Convert toml to list/dict
	sr_key = config_dict['sr_key']
	alias = config_dict['alias'].lower()
	planes = list(config_dict['planes'].values())
	sam_types = list(config_dict['sams'].values())
	ground_chance = config_dict['ground_chances']


	# Root window
	root = tk.Tk()
	root.title('GCI Trainer')
	root.geometry('850x500')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)

	# Init window content
	app = Window(root)


	# Set up env variables
	check_answer = threading.Event()		# Flag for if a solution check is requested by user
	new_problem = threading.Event()			# Flag for if a new problem is requested by user
	draw_radar = threading.Event()			# Flag for if a new radar screen needs to be drawn
	friend_list = LockVal([])				# Contains a list of all friendly planes on screen
	hostile_list = LockVal([])				# Contains a list of all hostile planes
	threat_list = LockVal([])				# Contains a list of all sam threats
	solution_vals = LockVal(())				# Contains relevant values for the solution

	problem_note = TranslateDict()
	problem_note[caution] = lambda: app.answers.select(0)
	problem_note[check_in] = lambda: app.answers.select(1)
	problem_note[threat] = lambda: app.answers.select(0)

	problem_func = do_nothing				# Set up dummy problem thread to prevent error on first problem
	problem = threading.Thread(target=problem_func)
	problem.start()


	# Main loop
	while True:
		try:
			root.state()
		except tk.TclError:
			break

		# Start new problem
		if new_problem.is_set():
			clear_vals()			# Clear old problem variables
			problem.join()			# Wait for old tts or sr to finish

			# Get and run new problem
			problem_func = app.settings.get_problem()
			problem_note[problem_func]()						# Set correct page in problem bar
			app.reset_answers()  								# Reset answer boxes and labels
			if problem_func in list(problem_note.keys()):
				problem = threading.Thread(target=problem_func)
				problem.start()

			new_problem.clear()		# Prevent infinite loop

		if check_answer.is_set():
			app.remove_corrections()
			if problem_func == caution:
				caution_answers()
			elif problem_func == check_in:
				check_in_answers()
			elif problem_func == threat:
				threat_answers()
			check_answer.clear()

		if draw_radar.is_set():
			app.draw_radar()
			draw_radar.clear()

		# Do tkinter
		root.update_idletasks()
		root.update()

	print('Preventing zombie threads')
	problem.join()
