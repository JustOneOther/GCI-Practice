from math import atan2, cos, degrees, radians, sin, sqrt
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
		return self.gen_entry.get().lower().replace(',', '')

	@property
	def check_answers(self):
		answers = [i.get() for i in self.check_entries]				# Get values from all boxes
		answers[-1] = answers[-1].lower().replace(',', '')			# Process text response
		answers[-2] = answers[-2].replace(',', '.')					# Process fuel decimal/comma
		answers.insert(5, ('selected' in self.guns.state()))		# Process checkbutton
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
		self.bind('<Enter>', func=self._on_enter)
		self.bind('<Leave>', func=self._on_exit)
		self.bind('<FocusIn>', func=self._focused)
		self.bind('<FocusOut>', func=self._unfocused)

	def prompt(self):
		"""
		Used to set box to default (on_exit) state
		"""
		self.delete(0, 'end')
		self.insert(0, self.text)
		# noinspection PyTypeChecker
		self.config(fg='#999999', justify=self.default_justify)

	def _focused(self, *args):
		self.is_focused = True
		if self.get() == self.text:		# Don't erase user data
			self.delete(0, 'end')
			self.config(fg='black', justify='left')

	def _unfocused(self, *args):
		self.is_focused = False
		self._on_exit()

	def _on_enter(self, *args):
		if self.get() == self.text:		# Don't erase user data
			self.delete(0, 'end')
			self.config(fg='black', justify=self.default_justify)

	def _on_exit(self, *args):
		if self.get() == '' and not self.is_focused:		# Don't erase user data
			self.insert(0, self.text)
			# noinspection PyTypeChecker
			self.config(fg='#999999', justify=self.default_justify)


class HoverText(tk.Label):
	def __init__(self, hover_text: str, master, *args, **kwargs):
		self.master = master
		super().__init__(master, *args, **kwargs)
		self.hover_text = hover_text
		self.bind('<Enter>', self._create_tip)
		self.bind('<Leave>', self._destroy_tip)

	def _create_tip(self, event):
		self.hover = tk.Toplevel(self)
		self.hover_label = tk.Label(self.hover, text=self.hover_text, bg='#dddddd', relief='solid', borderwidth=1)
		self.hover_label.grid(column=0, row=0, ipadx=1, ipady=1)
		self.hover.wm_overrideredirect(True)
		self.hover_label.update()
		try:			# Occasionally fails to get winfo_width of hover_label, maybe tkinter threading being wierd?
			pos = (self.winfo_rootx() - self.hover_label.winfo_width(), self.winfo_rooty() + self.winfo_height() // 2 - self.hover_label.winfo_height() // 2)
			self.hover.geometry(f"""+{pos[0]}+{pos[1]}""")
		except tk.TclError:
			self.hover.destroy()
			self.hover = None

	def _destroy_tip(self, event):
		if self.hover:
			self.hover.destroy()


class InfoBar(ttk.Frame):
	def __init__(self, version: str, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)		# Init frame

		# Configure columns & row
		self.columnconfigure(0, weight=0, minsize=125)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=0, minsize=125)
		self.rowconfigure(0, weight=1)

		# Set up objects
		self.status = ttk.Label(self, text='All good')
		self.program_label = ttk.Label(self, text='GCI Practice')
		self.version_label = ttk.Label(self, text=version)

		# Grid out objects
		self.status.grid(column=0, row=0, sticky='NSW')
		self.program_label.grid(column=1, row=0, sticky='NS')
		self.version_label.grid(column=2, row=0, sticky='NSE')


class ProblemManagement(ttk.Frame):
	def __init__(self, cmd_l: Callable, cmd_m: Callable, cmd_r: Callable, *args, **kwargs):
		super().__init__(*args, **kwargs)		# Init frame
		self.grid_propagate(False)

		self.error_labels = []

		# Configure rows and columns
		for i in range(3):
			self.columnconfigure(i, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=0, minsize=25)

		# Problem management buttons
		self.button_l = ttk.Button(self, text='Submit', command=cmd_l)
		self.button_m = ttk.Button(self, text='New', command=cmd_m)
		self.button_r = ttk.Button(self, text='Redraw', command=cmd_r)

		# Phrase correction
		self.errors = ()
		self.corrections = ttk.Frame(self)
		self.corrections.columnconfigure(0, weight=3, minsize=150)
		self.corrections.columnconfigure(1, weight=1)
		self.error_count = ttk.Label(self.corrections, text='')										# Error count text
		self.error_expand = ttk.Button(self.corrections, text='Show', command=self._expand_errors)  # Error expand button
		self.no_addr = HoverText('Expected: "<Name> <Num>-1, <Alias>"\nEx. "Simple 1-1, Magic"',    # Begin error label creation
								 self.corrections, text='No reciever or sender')
		self.call_id = HoverText('Expected: "<Name> <Num>-1, <Alias>"\nEx. "Simple 1-1, Magic"',
								 self.corrections, text='Incorrect plane address')
		self.self_id = HoverText('Expected: "<Name> <Num>-1, <Alias>"\nEx. "Simple 1-1, Magic"',
								 self.corrections, text='Incorrect self reference')
		self.sam_type = HoverText('Expected: "caution, <Name>"\nEx. "caution, sa-15"',
								  self.corrections, text='Incorrect SAM name')
		self.contact = HoverText('Expected negative or radar contact\nEx. "<Name> <Num>-1, <Alias>, radar contact"',
								 self.corrections, text='Contact erroniously reported')
		self.no_loc = HoverText('Expected BRAA or B/E\nEx. "braa 123 34 45 thousand, hot"',
								self.corrections, text='No location (BRAA or B/E) given')
		self.bad_braa = HoverText('Expected B/E location\nEx. "bullseye 123 for 34 at 45 thousand track south"',
								  self.corrections, text='Given BRAA instead of B/E')
		self.bad_bulls = HoverText('Expected BRAA location\nEx. "braa 123 34 45 thousand, hot"',
								   self.corrections, text='Given B/E instead of BRAA')
		self.bearing = HoverText('Given incorrect bearing\nEx. "braa <Bearing> 34 45 thousand, hot"',
								 self.corrections, text='Given incorrect bearing')
		self.distance = HoverText('Given incorrect distance\nEx. "braa 123 <Distance> 45 thousand, hot"',
								  self.corrections, text='Given incorrect distance')
		self.altitude = HoverText('Given incorrect altitude\nEx. "braa 123 34 <Altitude> thousand, hot"',
								  self.corrections, text='Given incorrect altitude')
		self.aspect = HoverText('Given incorrect aspcet\nEx. "braa 123 34 45 thousand, <Aspect>"',
								self.corrections, text='Given incorrect aspect')
		self.cardinal = HoverText('Given incorrect cardinal direction\nEx. "braa 123 34 45 thousand, flanking <Cardinal>"',
								  self.corrections, text='Given incorrect cardinal direction')
		self.caut_form = HoverText('Expected caution call format\nEx. "<Name> <Num>-1, <Alias>, caution <SAM>, <B/E data>"',
								   self.corrections, text='Given incorrect format')
		self.thr_form = HoverText('Expected threat call format\nEx. "<Name> <Num>-1, <Alias>, threat <BRAA data>, hostile"',
								  self.corrections, text='Given incorrect format')
		self.chk_form = HoverText('Expected check-in call format\nEx. "<Name> <Num>-1, <Alias>, (radar or negative) contact"',
								  self.corrections, text='Given incorrect format')
		self.error_labels = (self.call_id, self.self_id, self.sam_type, self.contact, self.no_loc, self.bad_braa,
							 self.bad_bulls, self.bearing, self.distance, self.altitude, self.aspect, self.cardinal,
							 self.caut_form, self.thr_form, self.chk_form)

		# Grid out
		self.corrections.grid(column=0, columnspan=3, row=0, sticky='NSEW')
		self.button_l.grid(column=0, row=1, sticky='NSEW')
		self.button_m.grid(column=1, row=1, sticky='NSEW')
		self.button_r.grid(column=2, row=1, sticky='NSEW')

	def write_errors(self, error_types: list):
		self.errors = tuple(error_types)
		self.error_count.config(text=f'{len(error_types)} errors detected')
		self.error_count.grid(column=0, row=0, sticky='NSW')
		self.error_expand.grid(column=1, row=0, sticky='EW')

	def _expand_errors(self):		# TODO: Re-write with pre-made error objects for hover labels
		row = 1
		if 'no_addr' in self.errors:
			self.no_addr.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'call_id' in self.errors:
			self.call_id.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'self_id' in self.errors:
			self.self_id.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'sam_type' in self.errors:
			self.sam_type.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'contact' in self.errors:
			self.contact.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'no_loc' in self.errors:
			self.no_loc.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'bad_braa' in self.errors:
			self.bad_braa.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'bad_bulls' in self.errors:
			self.bad_bulls.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'bearing' in self.errors:
			self.bearing.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'dist' in self.errors:
			self.distance.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'altitude' in self.errors:
			self.altitude.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'aspect' in self.errors:
			self.aspect.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'cardinal' in self.errors:
			self.cardinal.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'caut_form' in self.errors:
			self.caut_form.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'thr_form' in self.errors:
			self.thr_form.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1
		if 'chk_form' in self.errors:
			self.chk_form.grid(column=0, columnspan=2, row=row, sticky='NSW')
			row += 1


class RadarScreen(tk.Canvas):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)		# Create canvas

		# Set up turtle
		self.draw = turtle.RawTurtle(self)
		self.draw.speed(0)
		self.draw.hideturtle()
		self.draw.penup()

		# Init variables
		self.top_left = (-self.draw.screen.screensize()[0] // 2, self.draw.screen.screensize()[1] // 2)
		self.scalar = 1
		self.canv_size = (0, 0)
		self.canv_center = (0, 0)
		self.plane_center = (0, 0)
		self.planes = [(), (), ()]
		self.drawing = False
		self.ruler_down = False
		self.ruler_coords = (0, 0)
		self.bind('<Button-1>', func=self._ruler_place)

	def _bdraw_plane(self, plane) -> None:
		self.draw.goto(self.bullseye_pos[0], self.bullseye_pos[1])
		self.draw.setheading(90 - plane.bulls.bearing)
		self.draw.forward(plane.bulls.dist * self.scalar)
		self.draw.pendown()
		self.draw.dot(5)
		if plane.text:
			self.draw.write(f'{plane.text} - {plane.bulls.altitude}', font=('Arial', 11, 'normal'))
		else:
			self.draw.write(f'{plane.bulls.altitude}', font=('Arial', 11, 'normal'))
		self.draw.setheading(90 - plane.bulls.heading)
		self.draw.forward(plane.speed * self.scalar)
		self.draw.penup()

	def _get_center(self) -> None:
		self.canv_size = (self.winfo_width() - 5, self.winfo_height() - 6)
		self.canv_center = (self.top_left[0] + self.canv_size[0] / 2, self.top_left[1] - self.canv_size[1] / 2)

	def _ruler_place(self, event):
		if not self.drawing:		# Don't allow if drawing a page
			coords = (event.x + self.top_left[0] - 2, -event.y + self.top_left[1] + 2)		# Get mouse pos in draw reference
			if self.ruler_down:		# If first dot is down
				# Get coords, angle and distance in radar reference
				radar_coords = (coords[0] / self.scalar, coords[1] / self.scalar)
				dist = sqrt((radar_coords[0] - self.ruler_coords[1][0]) ** 2 + (radar_coords[1] - self.ruler_coords[1][1]) ** 2)
				ang = degrees(atan2(radar_coords[1] - self.ruler_coords[1][1], radar_coords[0] - self.ruler_coords[1][0]))

				# Draw line, text, and final dot
				self.draw.pendown()
				self.draw.goto((coords[0] + self.ruler_coords[0][0]) / 2, (coords[1] + self.ruler_coords[0][1]) / 2)
				self.draw.write(str(round((90 - ang) % 360, 1)) + '° | ' + str(round(dist, 1)) + ' NM',
								align='center', font=('Arial', 9, 'normal'))
				self.draw.goto(coords[0], coords[1])
				self.draw.dot(4, 'black')
				self.draw.penup()

				self.ruler_down = False		# Signal second dot down
			else:		# If first dot is not down
				# Go to first dot and draw it
				self.draw.goto(coords[0], coords[1])
				self.draw.pendown()
				self.draw.dot(4, 'black')
				self.draw.penup()

				self.ruler_coords = (coords, (coords[0] / self.scalar, coords[1] / self.scalar))   # Log canvas and radar coords
				self.ruler_down = True		# Signal second dot down

	def set_planes(self, allies, enemies, threats) -> None:
		self.planes = [enemies, allies, threats]

	def set_scalar(self) -> None:
		self._get_center()

		coords = [[0, 0]]
		for i in [plane for faction in self.planes for plane in faction]:
			coords.append((i.bulls.dist * cos(radians(90 - i.bulls.bearing)), i.bulls.dist * sin(radians(90 - i.bulls.bearing))))

		if coords != [[0, 0]]:  # Saves the calculations (and errors) if no plane is on screen
			# Calculates scalor
			x_range = (max([i[0] for i in coords]), min([i[0] for i in coords]))
			y_range = (max([i[1] for i in coords]), min([i[1] for i in coords]))
			self.plane_center = (sum(x_range) / 2, sum(y_range) / 2)
			great_scalar = max(((x_range[0] - x_range[1]) / self.canv_size[0], (y_range[0] - y_range[1]) / self.canv_size[1]))
			self.scalar = uniform(0.6, 0.9) / great_scalar
		else:
			self.plane_center = (0, 0)
			self.scalar = 1

	def draw_bulls(self) -> None:
		self.bullseye_pos = (self.canv_center[0] - (self.plane_center[0] * self.scalar),
						self.canv_center[1] - (self.plane_center[1] * self.scalar))
		self.draw.goto(self.bullseye_pos[0], self.bullseye_pos[1])
		self.draw.pendown()
		self.draw.dot(5)
		self.draw.penup()
		self.draw.sety(self.bullseye_pos[1] - round(2 * self.scalar))
		self.draw.pendown()
		self.draw.circle(round(2 * self.scalar), steps=6)
		self.draw.penup()

	def draw_planes(self) -> None:
		self.draw.color('red')
		for plane in self.planes[0]:
			self._bdraw_plane(plane)

		self.draw.color('blue')
		for plane in self.planes[1]:
			self._bdraw_plane(plane)

		self.draw.color('orange')
		for sam in self.planes[2]:
			self.draw.goto(self.bullseye_pos[0], self.bullseye_pos[1])
			self.draw.setheading(90 - sam.bulls.bearing)
			self.draw.forward(sam.bulls.dist * self.scalar)
			self.draw.pendown()
			self.draw.dot(5)
			self.draw.write(sam.text, font=('Arial', 11, 'normal'))
			self.draw.penup()
			self.draw.setheading(270)
			self.draw.forward(sam.fire_range * self.scalar)
			self.draw.setheading(0)
			self.draw.pendown()
			self.draw.circle(sam.fire_range * self.scalar, steps=35)
			self.draw.penup()

		self.draw.color('black')


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
		self.tts_wpm = ttk.Spinbox(self, from_=150, to=300, increment=10,
								   command=lambda: wpm_func(int(self.tts_wpm.get())), width=10)
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

