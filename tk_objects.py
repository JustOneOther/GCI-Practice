from math import cos, radians, sin
from random import choice, uniform
from tkinter import ttk
from typing import Callable
import tkinter as tk
import turtle


class AnswerBox(ttk.Notebook):
	def __init__(self, sr_key: str, *args, **kwargs):
		super().__init__(*args, **kwargs)			# Init notebook

		# Set up general answer page
		self.gen_page = tk.Frame(self)						# Create frame
		self.gen_page.columnconfigure(0, weight=1)			# Configure columns/rows
		self.gen_page.rowconfigure(0, weight=1)
		self.gen_page.rowconfigure(1, weight=1)
		self.gen_entry = DefaultEntry('Enter call here or use speech recognition', self.gen_page, default_justify='left')
		self.gen_text = tk.Label(self.gen_page, text=f'For speech recognition press {sr_key}')			# Instruction label
		self.add(self.gen_page, text='General')										# Add page to notebook
		self.gen_entry.grid(column=0, row=0, sticky='NSEW', padx=5, pady=5)			# Grid out page elements
		self.gen_text.grid(column=0, row=1, sticky='W', padx=5, pady=5)

		# Set up check-in page
		self.check_page = tk.Frame(self)			# Create frame
		for i in range(7):			# Configure columns/rows
			self.check_page.columnconfigure(i, weight=1, minsize=80)
		for i in range(3):
			self.check_page.rowconfigure(i, weight=1)
		self.flight_name = DefaultEntry('Flight X-X', self.check_page)			# Add answer boxes
		self.plane_type = ttk.Combobox(self.check_page)
		self.plane_type['values'] = ['F-16', 'F-18', 'JF-17']
		self.mission_type = ttk.Combobox(self.check_page)
		self.mission_type['values'] = ['BAI', 'CAP', 'SEAD', 'Strike']
		self.bullseye = DefaultEntry('BBB/RR', self.check_page)
		self.foxs = DefaultEntry('X X X', self.check_page)
		self.guns = ttk.Checkbutton(self.check_page)
		self.guns.state(['!alternate'])
		self.fuel = DefaultEntry('XX.X', self.check_page)
		self.check_entry = DefaultEntry('Enter response here or use speech recognition', self.check_page, default_justify='left')
		self.check_entries = [self.flight_name, self.plane_type, self.mission_type, self.bullseye, self.foxs]
		self.answer_boxes = [self.gen_entry, self.flight_name, self.plane_type, self.mission_type,
							 self.bullseye, self.foxs, self.fuel, self.check_entry]

		self.flight_label = tk.Label(self.check_page, text='Flight name')			# Add answer labels
		self.plane_label = tk.Label(self.check_page, text='Plane type')
		self.mission_label = tk.Label(self.check_page, text='Mission type')
		self.bullseye_label = tk.Label(self.check_page, text='Alpha check')
		self.foxs_label = tk.Label(self.check_page, text='Missile count')
		self.guns_label = tk.Label(self.check_page, text='Guns')
		self.fuel_label = tk.Label(self.check_page, text='Fuel state')
		self.check_entry_label = tk.Label(self.check_page, text=f'For speech recognition press {sr_key}')
		self.labels = [self.flight_label, self.plane_label, self.mission_label, self.bullseye_label,
					   self.foxs_label, self.guns_label, self.fuel_label]

		for i in range(len(self.check_entries)):								# Grid all entry boxes before guns
			self.check_entries[i].grid(column=i, row=1, sticky='EW')
		self.guns.grid(column=5, row=1)											# Grid remaining boxes
		self.fuel.grid(column=6, row=1, sticky='EW')
		self.check_entries += [self.fuel, self.check_entry]			# Add remaining boxes into check in answers
		for i in range(len(self.labels)):										# Grid all labels
			self.labels[i].grid(column=i, row=0, sticky='NSEW')
		self.labels += [self.check_entry_label, self.gen_text]
		self.check_entry.grid(column=0, columnspan=4, row=2, sticky='EW', padx=2)			# Grid check-in entry stuff
		self.check_entry_label.grid(column=4, columnspan=3, row=2, sticky='NSEW', padx=2)
		self.add(self.check_page, text='Check-in')			# Add page to notebook

	@property
	def gen_answers(self):
		return [word.strip(',').lower() for word in self.gen_entry.get().split(' ')]

	@property
	def check_answers(self):
		answers = [i.get() for i in self.check_entries]			# Get values from all boxes
		answers[-1] = [word.strip(',').lower() for word in answers[-1].split(' ')]			# Process response
		answers[-2] = answers[-2].replace(',', '.')
		answers.insert(5, ('selected' in self.guns.state()))
		return answers

	def reset_colors(self):
		for label in self.labels:
			label.config(fg='black')


class DefaultEntry(tk.Entry):
	"""
	Inherits from tk.Entry, contains a default message that is removed on hover or keyboard focus
	"""
	def __init__(self, text: str, *args, **kwargs):
		# Do justify bits
		try:
			self.default_justify = kwargs['default_justify']
			kwargs.pop('default_justify')
		except KeyError:
			self.default_justify = 'center'

		super().__init__(*args, **kwargs)		# Init entry

		# Inital config and binding
		self.master = args[0]
		self.config(fg='#999999', justify=self.default_justify)
		self.text = text
		self.is_focused = False
		self.insert(0, self.text)
		self.bind('<Enter>', func=self.on_enter)
		self.bind('<Leave>', func=self.on_exit)
		self.bind('<FocusIn>', func=self.focused)
		self.bind('<FocusOut>', func=self.unfocused)

	def prompt(self):
		"""
		Used to set box to default (on_exit) state
		"""
		self.delete(0, 'end')
		self.insert(0, self.text)
		# noinspection PyTypeChecker
		self.config(fg='#999999', justify=self.default_justify)
		self.master.focus()

	def focused(self, *args):
		self.is_focused = True
		if self.get() == self.text:		# Don't erase user data
			self.delete(0, 'end')
			self.config(fg='black', justify='left')

	def unfocused(self, *args):
		self.is_focused = False
		self.on_exit()

	def on_enter(self, *args):
		if self.get() == self.text:		# Don't erase user data
			self.delete(0, 'end')
			self.config(fg='black', justify=self.default_justify)

	def on_exit(self, *args):
		if self.get() == '' and not self.is_focused:		# Don't erase user data
			self.insert(0, self.text)
			# noinspection PyTypeChecker
			self.config(fg='#999999', justify=self.default_justify)


class InfoBar(ttk.Frame):
	def __init__(self, button1_cmd: Callable, button2_cmd: Callable, version: str, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)		# Init frame

		# Configure columns & row
		for i in [0, 1, 3]:
			self.columnconfigure(i, weight=0)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=1)

		# Set up objects
		self.button1 = ttk.Button(self, text='Draw Frame', command=button1_cmd)
		self.button2 = ttk.Button(self, text='Test Canvas', command=button2_cmd)
		self.program_label = ttk.Label(self, text='GCI Practice')
		self.version_label = ttk.Label(self, text=version)

		# Grid out objects
		self.button1.grid(column=0, row=0, sticky='NSW')
		self.button2.grid(column=1, row=0, sticky='NSW')
		self.program_label.grid(column=2, row=0, sticky='NS')
		self.version_label.grid(column=3, row=0, sticky='NSE')


class ProblemManagement(ttk.Frame):
	def __init__(self, cmd_l: Callable, cmd_m: Callable, cmd_r: Callable, *args, **kwargs):
		super().__init__(*args, **kwargs)		# Init frame
		self.grid_propagate(False)

		self.aspect_shorthand = {'hot': 'H', 'flanking': 'F', 'beaming': 'B', 'drag': 'D', None: 'N/A'}

		# Configure rows and columns
		for i in range(3):
			self.columnconfigure(i, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=0, minsize=25)

		# Problem management buttons
		self.button_l = ttk.Button(self, text='Submit', command=cmd_l)
		self.button_m = ttk.Button(self, text='New', command=cmd_m)
		self.button_r = ttk.Button(self, text='Redraw', command=cmd_r)

		# Table / TBD
		self.table = ttk.Notebook(self)

		self.braa = ttk.Frame(self)				# Set up pages
		self.bulls = ttk.Frame(self)
		for page in [self.braa, self.bulls]:    # Configure rows and columns
			for i in range(4):
				page.columnconfigure(i, weight=1)
			for i in range(8):
				page.rowconfigure(i, weight=1)
			ttk.Label(page, text='Bearing').grid(column=0, row=0, sticky='NSEW')				# Grid out shared headers
			ttk.Label(page, text='Range').grid(column=1, row=0, sticky='NSEW')
			ttk.Label(page, text='Altitude').grid(column=2, row=0, sticky='NSEW')
		ttk.Label(self.bulls, text='Heading').grid(column=3, row=0, sticky='NSEW')				# Grid out individual headers
		ttk.Label(self.braa, text='Aspect').grid(column=3, row=0, sticky='NSEW')

		self.bulls_table = [[ttk.Label(self.bulls) for __ in range(4)] for _ in range(7)]		# Set up label tables
		self.braa_table = [[ttk.Label(self.braa) for __ in range(4)] for _ in range(7)]
		for page in [self.bulls_table, self.braa_table]:			# Grid out labels
			for i in range(len(page)):
				for j in range(len(page[0])):
					page[i][j].grid(column=j, row=i + 1)

		self.table.add(self.bulls, text='Bullseye')
		self.table.add(self.braa, text='BRAA')

		# Grid out
		self.table.grid(column=0, columnspan=3, row=0, sticky='NSEW')
		self.button_l.grid(column=0, row=1, sticky='NSEW')
		self.button_m.grid(column=1, row=1, sticky='NSEW')
		self.button_r.grid(column=2, row=1, sticky='NSEW')

	def update_bulls(self, bulls_list) -> None:
		for (row, bulls) in zip(self.bulls_table, bulls_list):
			row[0].config(text=bulls.bearing)
			row[1].config(text=bulls.dist)
			row[2].config(text=bulls.altitude)
			row[3].config(text=bulls.heading)

	def update_braa(self, braa_list) -> None:
		for (row, braa) in zip(self.braa_table, braa_list):
			row[0].config(text=braa.bearing)
			row[1].config(text=braa.dist)
			row[2].config(text=braa.altitude)
			row[3].config(text=self.aspect_shorthand[braa.aspect])


class RadarScreen(tk.Canvas):
	def __init__(self, disable_buttons: tuple, *args, **kwargs):
		super().__init__(*args, **kwargs)		# Create canvas

		# Set up turtle
		self.draw = turtle.RawTurtle(self)
		self.draw.speed(0)
		self.draw.hideturtle()
		self.draw.penup()

		# Init variables
		self.affect_buttons = disable_buttons
		self.top_left = (-self.draw.screen.screensize()[0] // 2, self.draw.screen.screensize()[1] // 2)
		self.scalar = 0
		self.canv_size = (0, 0)
		self.center = (0, 0)

	def _get_center(self) -> None:
		self.canv_size = (self.winfo_width() - 5, self.winfo_height() - 6)
		self.center = (self.top_left[0] + self.canv_size[0] / 2, self.top_left[1] - self.canv_size[1] / 2)

	def border(self) -> None:
		# Disable affector buttons
		for button in self.affect_buttons:
			button.config(state='disabled')

		# Operation
		self._get_center()
		self.draw.goto(self.top_left[0], self.top_left[1])
		self.draw.pendown()
		self.draw.goto(self.top_left[0], self.top_left[1] - self.canv_size[1])
		self.draw.goto(self.top_left[0] + self.canv_size[0], self.top_left[1] - self.canv_size[1])
		self.draw.goto(self.top_left[0] + self.canv_size[0], self.top_left[1])
		self.draw.goto(self.top_left[0], self.top_left[1])
		self.draw.penup()

		# Enable affector buttons
		for button in self.affect_buttons:
			button.config(state='active')

	def _bdraw_plane(self, plane, i: int, bullseye_pos: tuple[float, float], scalar: float) -> None:
		self.draw.goto(bullseye_pos[0], bullseye_pos[1])
		self.draw.setheading(90 - plane.bulls.bearing)
		self.draw.forward(plane.bulls.dist * scalar)
		self.draw.pendown()
		self.draw.dot(5)
		if plane.text:
			self.draw.write(f'{i} - {plane.text}', font=('Arial', 11, 'normal'))
		else:
			self.draw.write(f'{i}', font=('Arial', 11, 'normal'))
		self.draw.setheading(90 - plane.bulls.heading)
		self.draw.forward(plane.speed * scalar)
		self.draw.penup()

	def b_draw(self, allies: list, enemies: list, threats: list) -> None:
		# Disable affector buttons
		for button in self.affect_buttons:
			button.config(state='disabled')

		# Clears drawer
		self.draw.clear()
		self.draw.setheading(0)

		# Updates canvas size
		self._get_center()

		# Process allies, enemies, and threats into coords for scaling
		coords = [[0, 0]]
		for i in allies + enemies + threats:
			coords.append((i.bulls.dist * cos(radians(90 - i.bulls.bearing)), i.bulls.dist * sin(radians(90 - i.bulls.bearing))))

		if coords != [[0, 0]]:			# Saves the calculations (and errors) if no plane is on screen
			# Calculates scalor
			x_range = (max([i[0] for i in coords]), min([i[0] for i in coords]))
			y_range = (max([i[1] for i in coords]), min([i[1] for i in coords]))
			great_scalor = max(((x_range[0] - x_range[1]) / self.canv_size[0], (y_range[0] - y_range[1]) / self.canv_size[1]))
			scalar = uniform(0.6, 0.9) / great_scalor

			# Get bullseye position and draw
			plane_center = (sum(x_range) / 2, sum(y_range) / 2)
			bullseye_pos = (self.center[0] - (plane_center[0] * scalar), self.center[1] - (plane_center[1] * scalar))
			self.draw.goto(bullseye_pos[0], bullseye_pos[1])
			self.draw.pendown()
			self.draw.dot(5)
			self.draw.penup()
			self.draw.sety(bullseye_pos[1] - round(2 * scalar))
			self.draw.pendown()
			self.draw.circle(round(2 * scalar), steps=6)
			self.draw.penup()

			# Draw enemies, allies, and threats
			i = 1
			self.draw.color('red')
			for plane in enemies:
				self._bdraw_plane(plane, i, bullseye_pos, scalar)
				i += 1

			self.draw.color('blue')
			for plane in allies:
				self._bdraw_plane(plane, i, bullseye_pos, scalar)
				i += 1

			self.draw.color('orange')
			for sam in threats:
				self.draw.goto(bullseye_pos[0], bullseye_pos[1])
				self.draw.setheading(90 - sam.bulls.bearing)
				self.draw.forward(sam.bulls.dist * scalar)
				self.draw.pendown()
				self.draw.dot(5)
				self.draw.write(sam.text, font=('Arial', 11, 'normal'))
				self.draw.penup()
				self.draw.setheading(270)
				self.draw.forward(sam.fire_range * scalar)
				self.draw.setheading(0)
				self.draw.pendown()
				self.draw.circle(sam.fire_range * scalar, steps=35)
				self.draw.penup()

			self.draw.color('black')
		else:			# Else for if no planes on screen
			self.draw.goto(self.center[0], self.center[1])
			self.draw.pendown()
			self.draw.dot(5)
			self.draw.penup()
			self.draw.sety(self.center[1] - 10)
			self.draw.pendown()
			self.draw.circle(10, steps=6)
			self.draw.penup()

		# Enable affector buttons
		for button in self.affect_buttons:
			button.config(state='active')


class SettingsBox(ttk.Frame):
	def __init__(self, wpm_func: Callable, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)		# Init frame
		self.grid_propagate(False)

		# Configure columns and rows
		self.columnconfigure(0, weight=1, minsize=70)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=0)
		for i in range(3):
			self.rowconfigure(i, weight=1)
		self.rowconfigure(3, weight=0)

		# Set up checkbuttons and spinbox
		self.check_in_button = ttk.Checkbutton(self, text='Check-in')
		self.check_in_button.state(['!alternate'])
		self.threat_button = ttk.Checkbutton(self, text='Threat')
		self.threat_button.state(['!alternate'])
		self.caution_button = ttk.Checkbutton(self, text='Caution')
		self.caution_button.state(['!alternate'])
		self.problem_buttons = [self.check_in_button, self.threat_button, self.caution_button]
		self.wpm_label = ttk.Label(self, text='TTS WPM')
		self.tts_wpm = ttk.Spinbox(self, from_=150, to=300, command=lambda: wpm_func(int(self.tts_wpm.get())), width=10)
		self.tts_wpm.set(200)

		# Grid out objects
		for i in range(len(self.problem_buttons)):
			self.problem_buttons[i].grid(column=0, columnspan=2, row=i, sticky='NSW', padx=5)
		self.wpm_label.grid(column=0, row=3, sticky='NSEW', padx=5)
		self.tts_wpm.grid(column=1, row=3, sticky='NSEW', padx=5)

		# Set button functions
		self.problem_dict = {}
		self.no_prob = None

	def set_funcs(self, check_in_func: Callable, threat_func: Callable, caution_func: Callable, no_prob: Callable) -> None:
		self.problem_dict[self.check_in_button] = check_in_func
		self.problem_dict[self.threat_button] = threat_func
		self.problem_dict[self.caution_button] = caution_func
		self.no_prob = no_prob

	def get_problem(self) -> Callable:
		available_problems = [i for i in self.problem_buttons if 'selected' in i.state()]
		if available_problems:
			return self.problem_dict[choice(available_problems)]
		else:
			return self.no_prob

