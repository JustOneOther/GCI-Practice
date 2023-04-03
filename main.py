try:
	from Scripts.GCI_structures import Braa, Bulls, Response, TranslateDict
	from math import asin, atan2, cos, degrees, radians, sin, sqrt
	from multiprocessing import Process
	from random import choice, choices, randint, uniform
	from tkinter import ttk
	from typing import Literal
	import tkinter as tk
	import tomllib as tom
	from Scripts import tk_objects, tts_sr
except ImportError as err:
	from time import sleep
	print('Please make sure you have all packages installed')
	print('If you do, please send the following information to #bugs in Damsel\'s server:')
	print(type(err), '|', err.args)
	sleep(20)
	raise Exception('Installation error')


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
		self.sign = manager.avail_signs.pop(randint(0, len(manager.avail_signs) - 1))
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
			cardinal_str = cardinal_translate[int(((heading + 22.5) // 45) % 8)]
			self.braa = Braa(bearing_r, randint(target.dist + 8, target.dist + 40), randint(10, 40), heading, asp_str, cardinal_str)
			self.bulls = braa_to_bulls(bullseye, self.braa)
		elif gen_mode == 'f_braa':			# If looking for friendly plane in a braa situation
			rough_bearing_r = randint(bullseye.heading - 225, bullseye.heading - 105)
			bearing_r = rough_bearing_r % 360
			bearing_rel_h = rough_bearing_r - bullseye.heading
			heading = randint(0, 359)
			asp = abs((bearing_rel_h - 180) - (heading - bullseye.heading))		# Gets integer aspect of targe
			asp_str = aspect_translate[abs(((180 - asp) % 360 - 180) // 30 + 0.5)]		# Translates interger aspect to string
			cardinal_str = cardinal_translate[int(((heading + 22.5) // 45) % 8)]
			self.braa = Braa(bearing_r, randint(15, 50), randint(10, 40), heading, asp_str, cardinal_str)
			self.bulls = braa_to_bulls(bullseye, self.braa)

		self.speed = round(uniform(2, 10), 1)


class LoadoutPlane(Plane):
	def __init__(self):
		super().__init__(info_text=False)
		self.count = randint(1, 4)
		model = choice(planes)
		self.name = model['name']
		self.guns = choices(['plus', 'minus'], weights=[.8, .2])[0]
		self.guns_bool = (self.guns == 'plus')
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


class ProblemManager:
	def __init__(self):
		self.friend_list = []
		self.hostile_list = []
		self.threat_list = []
		self.solution_vals = []
		with open('Resources/callsigns.txt', 'r') as file:
			self.avail_signs = file.read().split(', ')
			self.callsigns = tuple(self.avail_signs)

		self.tts_thread = Process(target=do_nothing)
		self.tts_thread.start()

		self.problem_type = ''
		self.prob_func_dict = {'Caution': self._caution, 'Threat': self._threat, 'Check-in': self._check_in}
		self.prob_ans_dict = {'Caution': self._caut_answers, 'Threat': self._threat_answers, 'Check-in': self._check_in_answers}

	# ---------- Problem types ----------

	def _caution(self):
		sol_plane = Plane()							# Generate answers
		sol_sam = Sam(sol_plane.bulls)
		self._generate_sides(sol_plane, sol_sam)    # Generate planes
		self.friend_list.insert(randint(0, len(self.friend_list)), sol_plane)			# Insert friendly for draw
		self.threat_list = [sol_plane]				# Insert sam for draw
		self.solution_vals = (sol_plane, sol_sam)   # Set solution values
		app.draw_radar()

	def _threat(self):
		sol_plane = Plane()
		sol_enemy = Plane('t_braa', bullseye=sol_plane.bulls)
		self._generate_sides(sol_plane, sol_enemy)
		self.friend_list.insert(randint(0, len(self.friend_list)), sol_plane)
		self.hostile_list.insert(randint(0, len(self.hostile_list)), sol_enemy)
		self.solution_vals = (sol_plane, sol_enemy)
		app.draw_radar()

	def _check_in(self):
		sol_plane = LoadoutPlane()

		phrase = f"""
				{alias}, {sol_plane.sign} {trans_dict[sol_plane.num]} 1; {single_dict[sol_plane.count]} ship {sol_plane.name} \
				checking in for {sol_plane.mission}; bullseye {' '.join([i for i in sol_plane.bulls.readable])} for \
				{sol_plane.bulls.dist}; {sol_plane.foxs[0]} {sol_plane.foxs[1]} {sol_plane.foxs[2]}, {sol_plane.guns}, \
				{sol_plane.fuel // 10} decimal {sol_plane.fuel % 10}
				"""
		process = Process(target=tts_sr.tts_say, args=(phrase, tts_sr.tts_engine.getProperty('rate')))
		self.tts_thread = process
		process.start()

		dummy_threat = Plane('t_braa', bullseye=sol_plane.bulls)
		self._generate_sides(sol_plane, dummy_threat, text=False)

		if uniform(0, 1) >= 0.75:
			on_screen = False
		else:
			self.friend_list.insert(randint(0, len(self.friend_list)), sol_plane)
			on_screen = True

		self.solution_vals = (sol_plane, on_screen)
		app.draw_radar()

	# ---------- Problem Checkers ----------

	def _caut_answers(self):
		usr_ans = app.get_answers()
		sol_plane = self.solution_vals[0]
		sol_sam = self.solution_vals[1]

		errors = self._check_addr(usr_ans, sol_plane)
		if usr_ans.sam_type not in {sol_sam.name.lower(), sol_sam.sign}:
			errors.append('sam_type')
		if usr_ans.braa:
			errors.append('bad_braa')
			errors += self._check_bulls_data(usr_ans.braa, sol_sam.braa, False)
		elif usr_ans.bulls:
			errors += self._check_bulls_data(usr_ans.bulls, sol_sam.bulls, False)
		else:
			errors.append('no_loc')
		if not usr_ans.form:
			errors.append('caut_form')

		app.set_corrections(errors, sol_plane, sol_sam)

	def _threat_answers(self):
		usr_ans = app.get_answers()
		sol_plane = self.solution_vals[0]
		sol_enemy = self.solution_vals[1]

		errors = self._check_addr(usr_ans, sol_plane)
		if usr_ans.bulls:
			errors.append('bad_bulls')
			errors += self._check_bulls_data(usr_ans.bulls, sol_enemy.bulls, True)
		elif usr_ans.braa:
			errors += self._check_bulls_data(usr_ans.braa, sol_enemy.braa, True)
		else:
			errors.append('no_loc')
		if not usr_ans.form:
			errors.append('thr_form')

		app.set_corrections(errors, sol_plane, sol_enemy)

	def _check_in_answers(self):
		usr_ans = app.get_answers()
		sol_plane = self.solution_vals[0]
		on_screen = self.solution_vals[1]

		errors = self._check_addr(usr_ans, sol_plane)
		if usr_ans.contact != on_screen:
			errors.append('contact')
		if on_screen:
			if [None, None, None] == [usr_ans.foxs, usr_ans.guns, usr_ans.fuel]:
				errors.append('no_state')
			else:
				if usr_ans.foxs != sol_plane.foxs:
					errors.append('foxs')
				if usr_ans.guns != sol_plane.guns_bool:
					errors.append('guns')
				if usr_ans.fuel != sol_plane.fuel:
					errors.append('fuel')
			if usr_ans.plane_count != single_dict[sol_plane.count]:
				errors.append('count')
			if usr_ans.model != sol_plane.name:
				errors.append('model')
			if usr_ans.mission:  # Make sure mission isn't NoneType
				if usr_ans.mission.lower() != sol_plane.mission.lower():
					errors.append('mission')
			else:
				errors.append('mission')
		if not usr_ans.form:
			errors.append('chk_form')

		app.set_corrections(errors, sol_plane, on_screen)

	# ---------- Sub-functions ----------

	@staticmethod
	def _check_addr(response: Response, solution: Plane) -> list:
		errors = []
		if not response.sign:
			errors.append('no_addr')
		else:
			if (response.sign, response.num) != (solution.sign, solution.num):
				errors.append('call_id')
			if response.alias != alias:
				errors.append('self_id')
		return errors

	@staticmethod
	def _check_bulls_data(response: Braa, solution, air: bool) -> list:
		errors = []
		if abs(response.bearing - solution.bearing) > 3:
			errors.append('bearing')
		if abs(response.dist - solution.dist) > 1:
			errors.append('dist')
		if air:
			if response.altitude != solution.altitude:
				errors.append('altitude')
			if response.aspect != solution.aspect:
				errors.append('aspect')
			if response.cardinal:
				if response.cardinal != solution.cardinal:
					errors.append('cardinal')
		return errors

	def _clear_vals(self):
		self.friend_list = []
		self.hostile_list = []
		self.threat_list = []
		self.solution_vals = []
		self.avail_signs = list(self.callsigns)

	def _generate_sides(self, origin, target, text=True):
		other_count = randint(0, 6)
		split = randint(0, other_count)
		self.friend_list = [Plane('f_braa', bullseye=origin.bulls, target=target.braa, info_text=text) for _ in range(split)]
		self.hostile_list = [Plane('h_braa', bullseye=origin.bulls, target=target.braa, info_text=text) for _ in range(other_count - split)]
		self.friend_list.insert(randint(0, split), origin)

	# ---------- Interface ----------

	def start_problem(self):
		self.tts_thread.join()
		self._clear_vals()   # Clear old problem variables
		app.reset_answers()  # Reset answer boxes and labels
		self.problem_type = app.settings.get_problem()
		self.prob_func_dict[self.problem_type]()

	def set_answers(self):
		app.remove_corrections()
		self.prob_ans_dict[self.problem_type]()


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
		self.infobar = tk_objects.InfoBar('v0.5.0-alpha', self)
		self.infobar.grid(column=0, row=0, sticky='NSEW', padx=5)

		# Problem management
		self.prob_man = tk_objects.ProblemManagement(manager.set_answers, manager.start_problem,
													 self.draw_radar, self, borderwidth=4, relief='ridge')
		self.prob_man.grid(column=1, row=2, rowspan=2, sticky='NSEW')

		# Canvas
		self.radar = tk_objects.RadarScreen(self)
		self.radar.grid(column=0, row=1, rowspan=2, sticky='NSEW')

		# Settings
		self.settings = tk_objects.SettingsBox(tts_sr.tts_set_speed, self, borderwidth=4, relief='ridge')
		self.settings.grid(column=1, row=0, rowspan=2, sticky='NSEW')

		# Answer bar
		self.answers = tk_objects.AnswerBox(sr_key, self)
		self.answers.grid(column=0, row=3, sticky='NSEW')

		# Vars
		self.canv_affectors = (self.prob_man.button_r, self.prob_man.button_m, self.prob_man.button_l)

		args[0].bind(f'<KeyPress-{sr_key.lower()}>', func=self._start_sr)
		args[0].bind(f'<KeyRelease-{sr_key.lower()}>', func=self._end_sr)

	# ---------- Internal functions ----------

	def _disable_canv_affectors(self):
		for button in self.canv_affectors:
			button.config(state='disabled')
		self.radar.drawing = True
		self.radar.ruler_down = False

	def _enable_canv_affectors(self):
		for button in self.canv_affectors:
			button.config(state='active')
		self.radar.drawing = False

	def _start_sr(self, event):
		if pysr_manager.rec_thread is None:
			self._disable_canv_affectors()
			pysr_manager.start_recording()

	def _end_sr(self, event):
		pysr_manager.stop_recording()
		self._enable_canv_affectors()
		text = pysr_manager.recognize_audio()
		self.answers.gen_entry.set_text(text)

	# ---------- Outward functions ----------

	def draw_radar(self):
		self.radar.set_planes(manager.friend_list, manager.hostile_list, manager.threat_list)
		self.radar.set_scalar()
		self._disable_canv_affectors()
		self.radar.draw.clear()
		self.radar.draw.setheading(0)
		self.radar.draw_bulls()
		self.radar.draw_planes()
		self._enable_canv_affectors()

	# ---------- Answer bits ----------

	def get_answers(self):
		if manager.problem_type == 'Caution':
			usr = self.answers.answer_box
			return Response(usr, r'\w+ \d-\d \w+ caution \S+ ((bullseye|b/e) \d{3}( for | |/)\d+|braa \d{3}( |/)\d+)$')
		elif manager.problem_type == 'Threat':
			usr = self.answers.answer_box
			return Response(usr, r'\w+ \d-\d \w+ threat ((bullseye|b/e) \d{3}( for |/| )\d+ (at )?\d+ thousand track \w+ hostile|braa \d{3}( |/)\d+ \d+ thousand \w+( \w+)? hostile)$')
		elif manager.problem_type == 'Check-in':
			usr = self.answers.answer_box
			usr = Response(usr, r'\w+ \d-\d \w+ (negative contact|radar contact (single|[2-4]) ship \S+ for \w+ \d \d \d (\+|-|plus|minus) \d+(\.|,)\d)$')
			return usr

	def reset_answers(self):
		self.answers.gen_text.config(fg='black')
		self.answers.gen_entry.prompt()
		self.remove_corrections()

	# ---------- Corrections ----------

	def remove_corrections(self):
		for label in self.prob_man.error_labels.values():
			label.grid_remove()
		self.prob_man.solution_exp.grid_remove()
		self.prob_man.error_expand.grid_remove()
		self.prob_man.error_count.grid_remove()
		self.prob_man.answer_label.grid_remove()

	def set_corrections(self, errors, ans1, ans2):
		self.prob_man.write_errors(errors)
		if errors:
			self.answers.gen_text.config(fg='red')
		else:
			self.answers.gen_text.config(fg='green')
		if manager.problem_type == 'Caution':
			self.prob_man.answer_text = f'{ans1.sign.capitalize()} {ans1.num}-1, {alias}, caution {ans2.text}, bullseye {ans2.bulls.readable} for {ans2.bulls.dist}'
		elif manager.problem_type == 'Threat':
			self.prob_man.answer_text = f'{ans1.sign.capitalize()} {ans1.num}-1, {alias}, threat braa {ans2.braa.readable}, {ans2.braa.dist}, {ans2.braa.altitude} thousand, {ans2.braa.aspect}, hostile'
		elif manager.problem_type == 'Check-in':
			if ans2:
				self.prob_man.answer_text = f'{ans1.sign.capitalize()} {ans1.num}-1, {alias}, radar contact {single_dict[ans1.count]} ship {ans1.name.upper()} for {ans1.mission}, {" ".join((str(i) for i in ans1.foxs))} {ans1.guns}, {ans1.fuel / 10}'
			else:
				self.prob_man.answer_text = f'{ans1.sign.capitalize()} {ans1.num}-1, {alias}, negative contact'


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


if __name__ == '__main__':
	# ---------- Common variables and configs ----------
	mission_types = ['CAP', 'BAI', 'Strike', 'SEAD']
	single_dict = {1: 'single', 2: '2', 3: '3', 4: '4'}
	trans_dict = TranslateDict()
	trans_dict[9] = 'niner'
	aspect_translate = {0.5: 'hot', 1.5: 'flanking', 2.5: 'beaming', 3.5: 'beaming', 4.5: 'drag', 5.5: 'drag'}
	cardinal_translate = {0: 'north', 1: 'northeast', 2: 'east', 3: 'southeast',
						  4: 'south', 5: 'southwest', 6: 'west', 7: 'northwest'}

	with open('Resources/config.toml', 'rb') as file:
		config_dict = tom.load(file)

	# Convert toml to list/dict
	sr_key = config_dict['sr_key']
	alias = config_dict['alias'].lower()
	planes = list(config_dict['planes'].values())
	sam_types = list(config_dict['sams'].values())
	ground_chance = config_dict['ground_chances']

	# ---------- Window setup and runtime ----------

	root = tk.Tk()
	root.title('GCI Trainer')
	root.geometry('850x500')
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)

	# Init window & probman classes
	pysr_manager = tts_sr.PySRHandler()
	manager = ProblemManager()
	app = Window(root)

	# Main loop
	root.mainloop()

	print('Preventing zombie threads')
	manager.tts_thread.join()
	if pysr_manager.rec_thread:
		while pysr_manager.rec_thread.is_alive():
			pysr_manager.rec_thread.join()
