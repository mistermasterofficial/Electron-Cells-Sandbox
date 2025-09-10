import pygame as pg
from cells import *
from settings_load import *
from threading import *

from modifications_manager import *
from open_file import *

import copy
import json
import os

from tkinter import *
from tkinter.messagebox import *
from tkinter import colorchooser
import tkinter as tk

from webbrowser import open_new

pg.init()

class Button:
	def __init__(self, name, x, y, second_name="", size=(settings["scale_ui_button"], settings["scale_ui_button"]), is_hotkey=False, hotkey=None, is_ctrl=False, is_shift=False, texture=pg.Surface((1,1)), settings=settings):
		self.name = name
		self.second_name = second_name

		self.rect = pg.Rect(x, y, size[0], size[1])

		self.is_active = True

		self.is_hotkey = is_hotkey
		if is_hotkey:
			self.hotkey = {"key":hotkey,"is_ctrl":is_ctrl,"is_shift":is_shift}

		self.texture = pg.transform.scale(texture, (size[0], size[1]))

		self.light_surface = pg.transform.scale(texture, (size[0], size[1]))
		self.dark_surface = pg.transform.scale(texture, (size[0], size[1]))

		light_color = pg.Color(settings["button_active_color"]["on_cursor"][0], settings["button_active_color"]["on_cursor"][1], settings["button_active_color"]["on_cursor"][2])
		dark_color = pg.Color(settings["button_active_color"]["on_press"][0], settings["button_active_color"]["on_press"][1], settings["button_active_color"]["on_press"][2])

		for x in range(self.texture.get_width()):
			for y in range(self.texture.get_height()):
				light_color.a, dark_color.a = self.texture.get_at((x, y)).a, self.texture.get_at((x, y)).a

				self.light_surface.set_at((x, y), light_color)
				self.dark_surface.set_at((x, y), dark_color)

		self.light_surface.set_alpha(settings["button_active_color"]["opacity"])
		self.dark_surface.set_alpha(settings["button_active_color"]["opacity"])

	def update(self, screen, textures, field, mouse, cursor_pos, current_tools, active_tool_number):
		screen.blit(pg.transform.scale(self.texture, (self.rect.width, self.rect.height)), self.rect)

		if self.second_name in current_tools:
			if self.second_name == current_tools[active_tool_number]:
				screen.blit(pg.transform.scale(textures["tool_cursor"], (self.rect.width, self.rect.height)), self.rect)
		elif "layer" in self.second_name:
			if int(self.second_name.split("layer")[0]) == field["data"]["active_layer_number"]:
				screen.blit(pg.transform.scale(textures["layer_cursor"], (self.rect.width, self.rect.height)), self.rect)

		if not self.is_active:
			screen.blit(self.dark_surface, self.rect)

		if self.rect.collidepoint(cursor_pos) and mouse[0]:
			screen.blit(self.dark_surface, self.rect)
		elif self.rect.collidepoint(cursor_pos):
			screen.blit(self.light_surface, self.rect)

	def is_pressed(self, event, cursor_pos):
		if self.is_active:
			if self.rect.collidepoint(cursor_pos):
				for e in event:
					if e.type == pg.MOUSEBUTTONDOWN:
						if e.button == 1:
							return True

			if self.is_hotkey:
				for e in event:
					if e.type == pg.KEYDOWN:
						if self.hotkey["is_ctrl"]:
							if e.key == self.hotkey["key"] and pg.key.get_mods() & pg.KMOD_CTRL:
								return True
						elif self.hotkey["is_shift"]:
							if e.key == self.hotkey["key"] and pg.key.get_mods() & pg.KMOD_SHIFT:
								return True
						else:
							if e.key == self.hotkey["key"]:
								return True
		return False

	def get_caption(self, cursor_pos):
		if self.rect.collidepoint(cursor_pos):
			return self.name
		else:
			return ""

def settings_dialog(settings):
	global current_tools

	global is_apply_settings

	is_apply_settings = False

	old_settings = copy.deepcopy(settings)

	root = Tk()
	root.title("Settings")
	root.minsize(width=500, height=400)
	root.iconphoto(True, PhotoImage(file="default_textures/icon.png"))
	root.resizable(0,0)

	def reset():
		global is_apply_settings
		is_reset_settings = askyesno("Reset settings", "Are you sure you want to reset all settings?")
		if is_reset_settings:
			reset_settings()
			showinfo("Reset settings", "Settings reset completed successfully!")
			is_apply_settings = True
			root.destroy()

	def exit_dialog():
		settings = old_settings
		root.destroy()
	
	def apply_settings():
		global is_apply_settings
		settings["is_visible_ui_caption"] = bool(is_visible_ui_caption.get())

		scale = scale_entry.get()
		try:
			scale = int(scale)
			settings["scale_ui_button"] = scale
		except Exception:
			pass

		opacity = opacity_entry.get()
		try:
			settings["button_active_color"]["opacity"] = max(0, min(int(opacity), 255))
		except Exception:
			pass

		if speed_val.get() != 2:
			settings["playback_speed"] = speed_options[speed_val.get()]
		else:
			try:
				settings["playback_speed"] = str(int(other_val_entry.get()))
			except Exception:
				pass
		
		settings["grid"]["mode"] = grid_options[grid_val.get()]
		try:
			settings["grid"]["opacity"] = max(0, min(int(grid_opacity_entry.get()), 255))
		except Exception:
			pass

		try:
			settings["selected_area_settings"]["opacity"] = max(0, min(int(area_opacity_entry.get()), 255))
		except Exception:
			pass
		
		settings["selected_texture_packs"] = list(active_packs_listbox.get(0, END))

		with open("settings.json", "w") as f:
			json.dump(settings, f)

		with open("cells_data.json", "r") as f:
			data = json.load(f)

		current_tools_list = current_tools_listbox.get(0, END)
		data["current_tools"].clear()

		for t in current_tools_list:
			if t in data["tools"]:
				data["current_tools"].append(t)

		with open("cells_data.json", "w") as f:
			json.dump(data, f, sort_keys=True, indent=4)

		is_apply_settings = True
		root.destroy()

	settings_points_list = {}

	settings_points_listbox = Listbox(relief=FLAT)
	settings_points_listbox.pack(side=LEFT, fill=BOTH, ipadx=20)

	frame_container = Frame()
	frame_container.pack(side=TOP, expand=True, fill=BOTH)
	frame_container.grid_rowconfigure(0, weight=1)
	frame_container.grid_columnconfigure(0, weight=1)

	apply_back_panel = Frame()
	apply_back_panel.pack(side=BOTTOM, fill=X, ipady=5)

	apply_btn = tk.Button(apply_back_panel, text="Apply", command=apply_settings)
	apply_btn.pack(side=RIGHT, fill=Y)

	back_btn = tk.Button(apply_back_panel, text="Back", command=exit_dialog)
	back_btn.pack(side=RIGHT, fill=Y)

	reset_btn = tk.Button(apply_back_panel, text="Reset", command=reset)
	reset_btn.pack(side=LEFT, fill=Y)

	# Colors

	def change_background_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["background_color"][0]), int(settings["background_color"][1]), int(settings["background_color"][2])))
		if color[0] is None:
			return
		settings["background_color"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
		field_background_color_label.config(text="Field background color is #{:02x}{:02x}{:02x}".format(int(settings["background_color"][0]), int(settings["background_color"][1]), int(settings["background_color"][2])))

	def change_on_cursor_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_cursor"][0]), int(settings["button_active_color"]["on_cursor"][1]), int(settings["button_active_color"]["on_cursor"][2])))
		if color[0] is None:
			return
		settings["button_active_color"]["on_cursor"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
		on_cursor_color_label.config(text="Button hover color is #{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_cursor"][0]), int(settings["button_active_color"]["on_cursor"][1]), int(settings["button_active_color"]["on_cursor"][2])))

	def change_on_press_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_press"][0]), int(settings["button_active_color"]["on_press"][1]), int(settings["button_active_color"]["on_press"][2])))
		if color[0] is None:
			return
		settings["button_active_color"]["on_press"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
		on_press_color_label.config(text="Button color when pressed is #{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_press"][0]), int(settings["button_active_color"]["on_press"][1]), int(settings["button_active_color"]["on_press"][2])))

	settings_colors_frame = Frame(frame_container)
	settings_colors_frame.grid(row=0, column=0, sticky="nsew")

	field_background_color_label = Label(settings_colors_frame, text="Field background color is #{:02x}{:02x}{:02x}".format(int(settings["background_color"][0]), int(settings["background_color"][1]), int(settings["background_color"][2])))
	field_background_color_label.pack()

	field_background_color_button = tk.Button(settings_colors_frame, text="Change color", command=change_background_color)
	field_background_color_button.pack()

	on_cursor_color_label = Label(settings_colors_frame, text="Button hover color is #{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_cursor"][0]), int(settings["button_active_color"]["on_cursor"][1]), int(settings["button_active_color"]["on_cursor"][2])))
	on_cursor_color_label.pack()

	on_cursor_color_button = tk.Button(settings_colors_frame, text="Change color", command=change_on_cursor_color)
	on_cursor_color_button.pack()

	on_press_color_label = Label(settings_colors_frame, text="Button color when pressed is #{:02x}{:02x}{:02x}".format(int(settings["button_active_color"]["on_press"][0]), int(settings["button_active_color"]["on_press"][1]), int(settings["button_active_color"]["on_press"][2])))
	on_press_color_label.pack()

	on_press_color_button = tk.Button(settings_colors_frame, text="Change color", command=change_on_press_color)
	on_press_color_button.pack()

	opacity_label = Label(settings_colors_frame, text="Button color opacity is")
	opacity_label.pack()

	opacity_entry = Entry(settings_colors_frame)
	opacity_entry.insert(END, str(settings["button_active_color"]["opacity"]))
	opacity_entry.pack()

	settings_points_list["Colors"] = settings_colors_frame

	# Caption

	def change_caption_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["ui_caption_color"][0]), int(settings["ui_caption_color"][1]), int(settings["ui_caption_color"][2])))
		if color[0] is None:
			return
		settings["ui_caption_color"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
		caption_color_label.config(text="Caption color is #{:02x}{:02x}{:02x}".format(int(settings["ui_caption_color"][0]), int(settings["ui_caption_color"][1]), int(settings["ui_caption_color"][2])))
	
	settings_caption_frame = Frame(frame_container)
	settings_caption_frame.grid(row=0, column=0, sticky="nsew")

	is_visible_ui_caption = IntVar()
	is_visible_ui_caption.set(int(settings["is_visible_ui_caption"]))

	caption_visible_check_btn = Checkbutton(settings_caption_frame, text="Caption visible", variable=is_visible_ui_caption)
	caption_visible_check_btn.pack()

	caption_color_label = Label(settings_caption_frame, text="Caption color is #{:02x}{:02x}{:02x}".format(int(settings["ui_caption_color"][0]), int(settings["ui_caption_color"][1]), int(settings["ui_caption_color"][2])))
	caption_color_label.pack()

	caption_color_btn = tk.Button(settings_caption_frame, text="Change color", command=change_caption_color)
	caption_color_btn.pack()

	settings_points_list["Caption"] = settings_caption_frame

	# Scale
	
	settings_scale_frame = Frame(frame_container)
	settings_scale_frame.grid(row=0, column=0, sticky="nsew")

	scale_ui_label = Label(settings_scale_frame, text="Scale is")
	scale_ui_label.pack()

	scale_entry = Entry(settings_scale_frame)
	scale_entry.insert(END, str(settings["scale_ui_button"]))
	scale_entry.pack()

	settings_points_list["Scale"] = settings_scale_frame

	# Speed

	speed_val = IntVar()

	if settings["playback_speed"]=="MAX":
		speed_val.set(0)
	elif settings["playback_speed"]=="FPS":
		speed_val.set(1)
	else:
		speed_val.set(2)

	settings_speed_frame = Frame(frame_container)
	settings_speed_frame.grid(row=0, column=0, sticky="nsew")

	speed_label = Label(settings_speed_frame, text="Playback speed is")
	speed_label.pack()

	speed_options = ["MAX", "FPS", ""]

	max_radiobutton = Radiobutton(settings_speed_frame, text="Max", variable=speed_val, value=0)
	max_radiobutton.pack()
	
	fps_radiobutton = Radiobutton(settings_speed_frame, text="Medium (recomended)", variable=speed_val, value=1)
	fps_radiobutton.pack()
	
	other_radiobutton = Radiobutton(settings_speed_frame, text="Other (ms)", variable=speed_val, value=2)
	other_radiobutton.pack()

	other_val_entry = Entry(settings_speed_frame)
	if not settings["playback_speed"] in ("MAX", "FPS"):
		other_val_entry.insert(END, str(settings["playback_speed"]))
	else:
		other_val_entry.config(state="disabled")
	other_val_entry.pack()

	settings_points_list["Speed"] = settings_speed_frame

	# Grid

	def change_grid_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["grid"]["color"][0]), int(settings["grid"]["color"][1]), int(settings["grid"]["color"][2])))
		if color[0] is None:
			return
		settings["grid"]["color"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]
	
	grid_val = IntVar()

	if settings["grid"]["mode"]=="HORIZONTAL":
		grid_val.set(0)
	elif settings["grid"]["mode"]=="VERTICAL":
		grid_val.set(1)
	else:
		grid_val.set(2)

	settings_grid_frame = Frame(frame_container)
	settings_grid_frame.grid(row=0, column=0, sticky="nsew")

	grid_label = Label(settings_grid_frame, text="Grid mode is")
	grid_label.pack()

	grid_options = ["HORIZONTAL", "VERTICAL", "CELL"]
	
	hor_radiobutton = Radiobutton(settings_grid_frame, text="Horizontal", variable=grid_val, value=0)
	hor_radiobutton.pack()
	
	vert_radiobutton = Radiobutton(settings_grid_frame, text="Vertical", variable=grid_val, value=1)
	vert_radiobutton.pack()

	cell_radiobutton = Radiobutton(settings_grid_frame, text="Cell", variable=grid_val, value=2)
	cell_radiobutton.pack()

	color_grid_btn = tk.Button(settings_grid_frame, text="Change grid color", command=change_grid_color)
	color_grid_btn.pack()

	grid_opacity_label = Label(settings_grid_frame, text="Grid opacity is")
	grid_opacity_label.pack()

	grid_opacity_entry = Entry(settings_grid_frame)
	grid_opacity_entry.insert(END, str(settings["grid"]["opacity"]))
	grid_opacity_entry.pack()

	settings_points_list["Grid"] = settings_grid_frame

	# Selection

	def change_area_color():
		color = colorchooser.askcolor(initialcolor="#{:02x}{:02x}{:02x}".format(int(settings["selected_area_settings"]["color"][0]), int(settings["selected_area_settings"]["color"][1]), int(settings["selected_area_settings"]["color"][2])))
		if color[0] is None:
			return
		settings["selected_area_settings"]["color"] = [int(color[0][0]), int(color[0][1]), int(color[0][2])]

	settings_selection_frame = Frame(frame_container)
	settings_selection_frame.grid(row=0, column=0, sticky="nsew")

	color_area_btn = tk.Button(settings_selection_frame, text="Change area color", command=change_area_color)
	color_area_btn.pack()

	area_opacity_label = Label(settings_selection_frame, text="Area opacity is")
	area_opacity_label.pack()

	area_opacity_entry = Entry(settings_selection_frame)
	area_opacity_entry.insert(END, str(settings["selected_area_settings"]["opacity"]))
	area_opacity_entry.pack()

	settings_points_list["Selection"] = settings_selection_frame

	# Texture packs

	def change_texture_packs():
		if disactive_packs_listbox.curselection()!=():
			disactive_pack_num = disactive_packs_listbox.curselection()[0]
			disactive_pack_name = disactive_packs_listbox.get(0, END)[disactive_pack_num]
			disactive_packs_listbox.delete(disactive_pack_num)
			active_packs_listbox.insert(END, disactive_pack_name)
		if active_packs_listbox.curselection()!=():
			active_pack_num = active_packs_listbox.curselection()[0]
			active_pack_name = active_packs_listbox.get(0, END)[active_pack_num]
			active_packs_listbox.delete(active_pack_num)
			disactive_packs_listbox.insert(END, active_pack_name)
	
	settings_texture_packs_frame = Frame(frame_container)
	settings_texture_packs_frame.grid(row=0, column=0, sticky="nsew")

	disactive_packs_frame = LabelFrame(settings_texture_packs_frame, text="Disactive texture packs")
	disactive_packs_frame.pack(side=LEFT, expand=True, fill=BOTH)
	active_packs_frame = LabelFrame(settings_texture_packs_frame, text="Active texture packs")
	active_packs_frame.pack(side=RIGHT, expand=True, fill=BOTH)

	scrollbar_for_disactive_packs_lisbox = Scrollbar(disactive_packs_frame, orient=VERTICAL)
	scrollbar_for_disactive_packs_lisbox.pack(side=RIGHT, fill=Y)
	disactive_packs_listbox = Listbox(disactive_packs_frame, yscrollcommand=scrollbar_for_disactive_packs_lisbox.set)
	disactive_packs_listbox.pack(expand=True, fill=BOTH)
	scrollbar_for_disactive_packs_lisbox.config(command=disactive_packs_listbox.yview)

	scrollbar_for_active_packs_lisbox = Scrollbar(active_packs_frame, orient=VERTICAL)
	scrollbar_for_active_packs_lisbox.pack(side=RIGHT, fill=Y)
	active_packs_listbox = Listbox(active_packs_frame, yscrollcommand=scrollbar_for_active_packs_lisbox.set)
	active_packs_listbox.pack(expand=True, fill=BOTH)
	scrollbar_for_active_packs_lisbox.config(command=active_packs_listbox.yview)

	for i in os.listdir("texture_packs"):
		if not os.path.isdir("texture_packs/" + i) or i in settings["selected_texture_packs"]:
			continue
		disactive_packs_listbox.insert(END, i)
	
	for i in settings["selected_texture_packs"]:
		active_packs_listbox.insert(END, i)

	settings_points_list["Texture packs"] = settings_texture_packs_frame

	# Tools

	def change_current_tools():
		if tools_listbox.curselection()!=():
			tools_num = tools_listbox.curselection()[0]
			tools_name = tools_listbox.get(0, END)[tools_num]
			tools_listbox.delete(tools_num)
			current_tools_listbox.insert(END, tools_name)
		if current_tools_listbox.curselection()!=() and len(current_tools_listbox.get(0, END))>1:
			current_tools_num = current_tools_listbox.curselection()[0]
			current_tools_name = current_tools_listbox.get(0, END)[current_tools_num]
			current_tools_listbox.delete(current_tools_num)
			tools_listbox.insert(END, current_tools_name)
		
	settings_tools_frame = Frame(frame_container)
	settings_tools_frame.grid(row=0, column=0, sticky="nsew")

	tools_frame = LabelFrame(settings_tools_frame, text="Other tools")
	tools_frame.pack(side=LEFT, expand=True, fill=BOTH)
	current_tools_frame = LabelFrame(settings_tools_frame, text="Current tools")
	current_tools_frame.pack(side=RIGHT, expand=True, fill=BOTH)

	scrollbar_for_tools_lisbox = Scrollbar(tools_frame, orient=VERTICAL)
	scrollbar_for_tools_lisbox.pack(side=RIGHT, fill=Y)
	tools_listbox = Listbox(tools_frame, yscrollcommand=scrollbar_for_tools_lisbox.set)
	tools_listbox.pack(expand=True, fill=BOTH)
	scrollbar_for_tools_lisbox.config(command=tools_listbox.yview)

	scrollbar_for_current_tools_lisbox = Scrollbar(current_tools_frame, orient=VERTICAL)
	scrollbar_for_current_tools_lisbox.pack(side=RIGHT, fill=Y)
	current_tools_listbox = Listbox(current_tools_frame, yscrollcommand=scrollbar_for_current_tools_lisbox.set)
	current_tools_listbox.pack(expand=True, fill=BOTH)
	scrollbar_for_current_tools_lisbox.config(command=current_tools_listbox.yview)

	with open("cells_data.json", "r") as f:
		data = json.load(f)
		all_tools = data["tools"]
		current_tools = data["current_tools"]

	for i in all_tools:
		if i in current_tools:
			continue
		tools_listbox.insert(END, i)
	
	for i in current_tools:
		current_tools_listbox.insert(END, i)

	settings_points_list["Tools"] = settings_tools_frame

	# Mods manager

	def delete_mods():
		if installed_mods_listbox.curselection()!=():
			mod_num = installed_mods_listbox.curselection()[0]
			uninstall_modifications(installed_mods_listbox.get(0, END)[mod_num])
			installed_mods_listbox.delete(mod_num)
	
	def install_mods():
		installed_mod = install_modifications(tk.filedialog.askopenfilename(filetypes=[("Mod JSON","*.json")]))
		if installed_mod[0]:
			installed_mods_listbox.insert(END, installed_mod[1])
		
	modifications_manager_frame = Frame(frame_container)
	modifications_manager_frame.grid(row=0, column=0, sticky="nsew")

	install_mods_frame = Frame(modifications_manager_frame)
	install_mods_frame.pack(side=LEFT, expand=True, fill=BOTH)
	installed_mods_frame = LabelFrame(modifications_manager_frame, text="Installed Mods")
	installed_mods_frame.pack(side=RIGHT, expand=True, fill=BOTH)

	install_mods_button = tk.Button(install_mods_frame, text="Install mods", command=install_mods)
	install_mods_button.pack(side=TOP)

	scrollbar_for_installed_mods_listbox = Scrollbar(installed_mods_frame, orient=VERTICAL)
	scrollbar_for_installed_mods_listbox.pack(side=RIGHT, fill=Y)
	installed_mods_listbox = Listbox(installed_mods_frame, yscrollcommand=scrollbar_for_installed_mods_listbox.set)
	installed_mods_listbox.pack(expand=True, fill=BOTH)
	scrollbar_for_installed_mods_listbox.config(command=installed_mods_listbox.yview)

	with open("cells_data.json", "r") as f:
		mods = json.load(f)["modifications"]
	
	for m in mods.keys():
		installed_mods_listbox.insert(END, m)

	settings_points_list["Modifications"] = modifications_manager_frame

	for i in settings_points_list:
		settings_points_listbox.insert(END, i)
	
	point_num = 0
	settings_points_list[settings_points_listbox.get(0, END)[point_num]].tkraise()

	root.update()
	width = root.winfo_width()
	height = root.winfo_height()
	x = int((root.winfo_screenwidth() / 2) - (width / 2))
	y = int((root.winfo_screenheight() / 2) - (height / 2))
	root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

	while True:
		try:
			current_point_num = settings_points_listbox.curselection()[0]

			if current_point_num != point_num:
				settings_points_list[settings_points_listbox.get(0, END)[current_point_num]].tkraise()
			
			point_num = current_point_num

			if speed_val.get()==2:
				other_val_entry.config(state="normal")
			else:
				other_val_entry.config(state="disabled")
		except Exception:
			pass

		try:
			change_current_tools()
		except Exception:
			pass

		try:
			change_texture_packs()
		except Exception:
			pass
			
		try:
			delete_mods()
		except Exception:
			pass

		try:
			root.update()
		except Exception:
			break
	
	root.mainloop()
	
	return is_apply_settings

def about_dialog(settings):
	def go_to(url):
		open_new(url)
	
	root = Tk()
	root.title("About")
	root.minsize(width=300, height=400)
	root.iconphoto(True, PhotoImage(file="default_textures/icon.png"))
	root.resizable(0,0)
	root.config(bg="#777777")

	ECS_logo = PhotoImage(file="default_textures/ui/ECSLogo.png")
	ECS_logo_label = Label(image=ECS_logo, cursor='hand1')
	ECS_logo_label.config(bg="#777777")
	ECS_logo_label.pack(expand=True)
	ECS_logo_label.bind("<Button-1>", lambda e: go_to("https://mistermasterofficial.github.io/Electron-Cells-Sandbox/"))

	info_label = Label(text="Electron Cells Sandbox. Fonts: Roboto, Geostar Fill.\n©Mister Master feat. Robotix 2021.\nAll rights reserved.", font="20", fg="#000000")	
	info_label.config(bg="#777777")
	info_label.pack(expand=True)

	MisterMaster_logo = PhotoImage(file="default_textures/ui/MisterMaster.png")
	MisterMaster_logo_label = Label(image=MisterMaster_logo, cursor='hand1')
	MisterMaster_logo_label.config(bg="#777777")
	MisterMaster_logo_label.pack(side=LEFT, expand=True)
	MisterMaster_logo_label.bind("<Button-1>", lambda e: go_to("https://mistermasterofficial.github.io/"))

	Robotix_logo = PhotoImage(file="default_textures/ui/Robotix.png")
	Robotix_logo_label = Label(image=Robotix_logo, cursor='hand1')
	Robotix_logo_label.config(bg="#777777")
	Robotix_logo_label.pack(side=RIGHT, expand=True)
	Robotix_logo_label.bind("<Button-1>", lambda e: go_to("https://robotix-com.web.app"))

	root.update()
	width = root.winfo_width()
	height = root.winfo_height()
	x = int((root.winfo_screenwidth() / 2) - (width / 2))
	y = int((root.winfo_screenheight() / 2) - (height / 2))
	root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

	root.mainloop()

def ask_dialog(caption, text):
	top = tkinter.Tk()
	top.iconphoto(True, tkinter.PhotoImage(file="default_textures/icon.png"))
	top.withdraw()
	confirm = askyesno(caption, text)
	top.destroy()
	return confirm

if __name__=="__main__":
	settings_dialog(load_settings_and_textures(names_cells)[0])