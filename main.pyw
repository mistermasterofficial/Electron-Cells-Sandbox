"""--------------------Imports & Initialising---------------------"""

import pygame as pg

from open_file import open_file
from save_file import *
from settings_load import *
from cells import *
from ui import *

import os
import json
import copy
from threading import *
from time import sleep

pg.init()

def thread(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

"""-----------------------------Start Programm-----------------------------------"""

field = create_field()

temp_data = []

FPS = 60

os.environ['SDL_VIDEO_CENTERED'] = '1'

run = True

screen = pg.display.set_mode((1024, 640), pg.RESIZABLE)

pg.display.set_caption("*new - Electron Cells Sandbox")

pg.display.set_icon(textures["icon"])

fps_main, fps_update, fps_field = 0, 0, 0

process = False

font_object = pg.font.Font(settings["font_path"], settings["scale_ui_button"])

is_visible_panels = True

is_grid_visible = False

is_axis_visible = False

area = Area(l=field["data"]["active_layer_number"])
is_selection_mode = False

copied_data = []

"""-----------------------------GUI-------------------------------"""

def create_elements_ui():
	global settings

	elements_ui = {}
	
	if is_visible_panels and not is_selection_mode:
		current_tools_panel = pg.Rect(0, 0, settings["scale_ui_button"]*len(current_tools), settings["scale_ui_button"])
		current_tools_panel.centerx = screen.get_rect().centerx
		current_tools_panel.bottom = screen.get_rect().bottom

		main_panel = pg.Rect(0, 0, settings["scale_ui_button"], settings["scale_ui_button"]*4)
		main_panel.centery = screen.get_rect().centery
		main_panel.left = screen.get_rect().left

		layers_panel = pg.Rect(0, 0, settings["scale_ui_button"], settings["scale_ui_button"]*len(field["data"]["layers"]))
		layers_panel.right = screen.get_rect().right
		layers_panel.centery = screen.get_rect().centery

		delete_layers_panel = pg.Rect(0, 0, settings["scale_ui_button"], settings["scale_ui_button"]*len(field["data"]["layers"]))
		delete_layers_panel.centery = screen.get_rect().centery
		delete_layers_panel.right = layers_panel.left

		playback_panel = pg.Rect(0, 0, settings["scale_ui_button"]*4, settings["scale_ui_button"])
		playback_panel.bottom = current_tools_panel.top
		playback_panel.centerx = current_tools_panel.centerx

		for i in range(len(current_tools)):
			try:
				elements_ui[current_tools[i]] = Button(current_tools[i][0].upper() + current_tools[i][1:] + " (LEFT or RIGHT)", current_tools_panel.x+settings["scale_ui_button"]*i, current_tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), second_name=current_tools[i], texture=textures[current_tools[i]], settings=settings)
			except KeyError:
				continue

		elements_ui["new_file"] = Button("New File (Ctrl + N)", main_panel.x, main_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["new_file"], is_hotkey=True, hotkey=pg.K_n, is_ctrl=True, settings=settings)

		elements_ui["open_file"] = Button("Open File (Ctrl + O)", main_panel.x, main_panel.y+settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["open_file"], is_hotkey=True, hotkey=pg.K_o, is_ctrl=True, settings=settings)

		elements_ui["save_file"] = Button("Save File (Ctrl + S)", main_panel.x, main_panel.y+settings["scale_ui_button"]*2, size=(settings["scale_ui_button"], settings["scale_ui_button"]),  texture=textures["save_file"], is_hotkey=True, hotkey=pg.K_s, is_ctrl=True, settings=settings)

		elements_ui["save_as_file"] = Button("Save as File (Shift + S)", main_panel.x, main_panel.y+settings["scale_ui_button"]*3, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["save_as_file"], is_hotkey=True, hotkey=pg.K_s, is_shift=True, settings=settings)

		for i in range(len(field["data"]["layers"])):
			elements_ui[f"{i}layer"] = Button(f"Layer Number {str(i+1)} (UP or DOWN)", layers_panel.x, layers_panel.bottom-settings["scale_ui_button"]*(i+1), size=(settings["scale_ui_button"], settings["scale_ui_button"]), second_name=f"{i}layers", texture=textures["layer"], settings=settings)

			elements_ui[f"{i}delete_layer"] = Button(f"Delete Layer Number {str(i+1)}", delete_layers_panel.x, delete_layers_panel.bottom-settings["scale_ui_button"]*(i+1), size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["delete_layer"], settings=settings)
		
		if len(field["data"]["layers"])<10:
			add_layer = pg.Rect(-settings["scale_ui_button"], -settings["scale_ui_button"], settings["scale_ui_button"], settings["scale_ui_button"], settings=settings)
			add_layer.bottom = layers_panel.top
			add_layer.right = screen.get_rect().right
			elements_ui["add_layer"] = Button("Add Layer", add_layer.x, add_layer.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["add_layer"], settings=settings)

		elements_ui["play"] = Button("Play (SPACE)", playback_panel.x+settings["scale_ui_button"], playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["play"], is_hotkey=True, hotkey=pg.K_SPACE, settings=settings)

		elements_ui["pause"] = Button("Pause (SPACE)", playback_panel.x+settings["scale_ui_button"]*2, playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["pause"], is_hotkey=True, hotkey=pg.K_SPACE, settings=settings)

		elements_ui["undo"] = Button("Undo (Ctrl + U)", playback_panel.x, playback_panel.y, texture=textures["undo"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), is_hotkey=True, hotkey=pg.K_u, is_ctrl=True, settings=settings)

		elements_ui["reproduce_one_step"] = Button("Reproduce one step (Ctrl + R)", playback_panel.x+settings["scale_ui_button"]*3, playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["reproduce_one_step"], is_hotkey=True, hotkey=pg.K_r, is_ctrl=True, settings=settings)

		elements_ui["about"] = Button("About", 0, 0, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["about"], settings=settings)

		elements_ui["hide_panels"] = Button("Hide Panels (Ctrl + H)", 0, screen.get_rect().bottom-settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["hide_panels"], is_hotkey=True, hotkey=pg.K_h, is_ctrl=True, settings=settings)

		elements_ui["settings"] = Button("Settings", 0, 0, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["settings"], settings=settings)
		elements_ui["settings"].rect.topright = screen.get_rect().topright

		elements_ui["selection_mode"] = Button("Selection mode", 0, 0, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["selection_mode"], settings=settings)
		elements_ui["selection_mode"].rect.bottomright = screen.get_rect().bottomright

	elif not is_visible_panels:
		layers_panel = pg.Rect(0, 0, settings["scale_ui_button"], settings["scale_ui_button"]*len(field["data"]["layers"]), settings=settings)
		layers_panel.right = screen.get_rect().right
		layers_panel.centery = screen.get_rect().centery

		playback_panel = pg.Rect(0, 0, settings["scale_ui_button"]*4, settings["scale_ui_button"], settings=settings)
		playback_panel.bottom = screen.get_rect().bottom
		playback_panel.centerx = screen.get_rect().centerx

		for i in range(len(current_tools)):
			try:
				elements_ui[current_tools[i]] = Button(current_tools[i][0].upper() + current_tools[i][1:] + " (LEFT or RIGHT)", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), second_name=current_tools[i], texture=textures[current_tools[i]], settings=settings)
			except KeyError:
				continue

		elements_ui["new_file"] = Button("New File (Ctrl + N)", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["new_file"], is_hotkey=True, hotkey=pg.K_n, is_ctrl=True, settings=settings)

		elements_ui["open_file"] = Button("Open File (Ctrl + O)", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["open_file"], is_hotkey=True, hotkey=pg.K_o, is_ctrl=True, settings=settings)

		elements_ui["save_file"] = Button("Save File (Ctrl + S)", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]),  texture=textures["save_file"], is_hotkey=True, hotkey=pg.K_s, is_ctrl=True, settings=settings)

		elements_ui["save_as_file"] = Button("Save as File (Shift + S)", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["save_as_file"], is_hotkey=True, hotkey=pg.K_s, is_shift=True, settings=settings)

		for i in range(len(field["data"]["layers"])):
			elements_ui[f"{i}layer"] = Button(f"Layer Number {str(i+1)} (UP or DOWN)", layers_panel.x, layers_panel.bottom-settings["scale_ui_button"]*(i+1), size=(settings["scale_ui_button"], settings["scale_ui_button"]), second_name=f"{i}layers", texture=textures["layer"], settings=settings)

		elements_ui["play"] = Button("Play (SPACE)", playback_panel.x+settings["scale_ui_button"], playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["play"], is_hotkey=True, hotkey=pg.K_SPACE, settings=settings)

		elements_ui["pause"] = Button("Pause (SPACE)", playback_panel.x+settings["scale_ui_button"]*2, playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["pause"], is_hotkey=True, hotkey=pg.K_SPACE, settings=settings)

		elements_ui["undo"] = Button("Undo (Ctrl + U)", playback_panel.x, playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["undo"], is_hotkey=True, hotkey=pg.K_u, is_ctrl=True, settings=settings)

		elements_ui["reproduce_one_step"] = Button("Reproduce one step (Ctrl + R)", playback_panel.x+settings["scale_ui_button"]*3, playback_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["reproduce_one_step"], is_hotkey=True, hotkey=pg.K_r, is_ctrl=True, settings=settings)

		elements_ui["about"] = Button("About", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["about"], settings=settings)

		elements_ui["settings"] = Button("Settings", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["settings"], settings=settings)

		elements_ui["show_panels"] = Button("Show Panels (Ctrl + H)", 0, screen.get_rect().bottom-settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["show_panels"], is_hotkey=True, hotkey=pg.K_h, is_ctrl=True, settings=settings)

		elements_ui["selection_mode"] = Button("Selection mode", -settings["scale_ui_button"], -settings["scale_ui_button"], size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["selection_mode"], settings=settings)

	else:
		tools_panel = pg.Rect(0, 0, settings["scale_ui_button"]*5, settings["scale_ui_button"], settings=settings)
		tools_panel.bottom = screen.get_rect().bottom
		tools_panel.centerx = screen.get_rect().centerx

		elements_ui["move_selected_area"] = Button("Move (Ctrl + M)", tools_panel.x+settings["scale_ui_button"]*0, tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["move_selected_area"], is_hotkey=True, hotkey=pg.K_m, is_ctrl=True, settings=settings)
		elements_ui["copy_selected_area"] = Button("Copy (Ctrl + C)", tools_panel.x+settings["scale_ui_button"]*1, tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["copy_selected_area"], is_hotkey=True, hotkey=pg.K_c, is_ctrl=True, settings=settings)
		elements_ui["paste_selected_area"] = Button("Paste (Ctrl + V)", tools_panel.x+settings["scale_ui_button"]*2, tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["paste_selected_area"], is_hotkey=True, hotkey=pg.K_v, is_ctrl=True, settings=settings)
		elements_ui["delete_selected_area"] = Button("Delete (Del)", tools_panel.x+settings["scale_ui_button"]*3, tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["delete_selected_area"], is_hotkey=True, hotkey=pg.K_DELETE, settings=settings)
		elements_ui["exit_from_selection_mode"] = Button("Exit (Esc)", tools_panel.x+settings["scale_ui_button"]*4, tools_panel.y, size=(settings["scale_ui_button"], settings["scale_ui_button"]), texture=textures["exit_from_selection_mode"], is_hotkey=True, hotkey=pg.K_ESCAPE, settings=settings)

		if area.is_selection or area.is_move:
			elements_ui["move_selected_area"].is_active = False
			elements_ui["copy_selected_area"].is_active = False
			elements_ui["paste_selected_area"].is_active = False
			elements_ui["delete_selected_area"].is_active = False
			elements_ui["exit_from_selection_mode"].is_active = False

		if len(area.data)==0:
			elements_ui["move_selected_area"].is_active = False
			elements_ui["copy_selected_area"].is_active = False
			elements_ui["delete_selected_area"].is_active = False

		if len(copied_data)==0:
			elements_ui["paste_selected_area"].is_active = False

	if not is_selection_mode:
		if not process:
			elements_ui["pause"].is_active = False

			if len(temp_data)==0:
				elements_ui["undo"].is_active = False
		else:

			for i in range(len(current_tools)):
				elements_ui[current_tools[i]].is_active = False

			elements_ui["new_file"].is_active = False

			elements_ui["open_file"].is_active = False

			elements_ui["save_file"].is_active = False

			elements_ui["save_as_file"].is_active = False

			for i in range(len(field["data"]["layers"])):
				if is_visible_panels:
					elements_ui[f"{i}delete_layer"].is_active = False

			if len(field["data"]["layers"])<10:
				if is_visible_panels:
					elements_ui["add_layer"].is_active = False

			elements_ui["play"].is_active = False

			elements_ui["undo"].is_active = False

			elements_ui["reproduce_one_step"].is_active = False

			elements_ui["about"].is_active = False

			elements_ui["settings"].is_active = False

			if is_visible_panels:
				elements_ui["hide_panels"].is_active = False
			else:
				elements_ui["show_panels"].is_active = False
			
			elements_ui["selection_mode"].is_active = False

	return elements_ui

def reload_ui():
	global elements_ui
	elements_ui = create_elements_ui()

reload_ui()

"""------------------------------Settings Reload--------------------------------"""

def reload_settings():
	global settings
	global textures
	global font_object
	global cells_textures
	global elements_ui
	global field
	global current_tools
	global names_cells
	global list_cells_rules
	global active_tool_number

	names_cells, list_cells_rules, current_tools = cells_load()
	
	if len(current_tools)==0:
		current_tools = ["eraser"]
	active_tool_number %= len(current_tools)

	settings, textures = load_settings_and_textures(names_cells)
	font_object = pg.font.Font(settings["font_path"], settings["scale_ui_button"])
	cells_textures = get_cells_texture(field["scale"], textures, names_cells)
	reload_ui()
	pg.display.set_icon(textures["icon"])

"""------------------------------Mouse & Key Control----------------------------"""

def control(event, mouse, cursor_pos):
	global is_visible_panels
	global active_tool_number
	global process
	global field
	global settings
	global elements_ui
	global start_position
	global temp_data
	global saved_field_coords
	global is_grid_visible
	global is_axis_visible
	global is_selection_mode
	global area
	global copied_data

	is_click_ui = False
	for i in elements_ui:
		if elements_ui[i].rect.collidepoint(cursor_pos):
			is_click_ui = True
			break
	
	for i in elements_ui:
		if elements_ui[i].is_pressed(event, cursor_pos):
			if i == "new_file":
				if ask_dialog("New File", "This file may not be saved. Are you sure you want to create a new file?"):
					temp_data.clear()
					field = create_field()
					pg.display.set_caption("*new - Electron Cells Sandbox")
					reload_ui()

			if i == "open_file":
				f, caption = open_file(field)
				if caption != "":
					field = create_field()
					field["data"], field["file_path"] = f["data"], f["file_path"]
					pg.display.set_caption(caption + " - Electron Cells Sandbox")
					temp_data.clear()
				reload_ui()

			if i == "save_file":
				field, caption = save_file(field)
				if caption != "":
					pg.display.set_caption(caption + " - Electron Cells Sandbox")

			if i == "save_as_file":
				file_path = copy.deepcopy(field["file_path"])
				field["file_path"] = ""
				f, caption = save_file(field)
				if caption != "":
					field = f
					pg.display.set_caption(caption + " - Electron Cells Sandbox")
				else:
					field["file_path"] = file_path

			if i == "play":
				temp_data.append(copy.deepcopy(field["data"]))
				process = True
				reload_ui()

			if i == "pause":
				process = False
				reload_ui()

			if i == "reproduce_one_step":
				temp_data.append(copy.deepcopy(field["data"]))
				saved_field_coords = [0, 0]
				saved_field_coords[0], saved_field_coords[1], field["data"]["layers"] = to_array(field["data"]["layers"])
				field["data"]["layers"] = cells_update(field["data"]["layers"], names_cells, list_cells_rules)
				field["data"]["layers"] = to_list(field["data"]["layers"], saved_field_coords[0], saved_field_coords[1])
				reload_ui()

			if i == "add_layer":
				field["data"]["layers"].append([])
				for cell in field["data"]["layers"][0]:
					if cell[2] == "elevator":
						field["data"]["layers"] = set_cell(field["data"]["layers"], len(field["data"]["layers"])-1, cell[0], cell[1], "elevator")
				reload_ui()

			elif "delete_layer" in i:
				layer_number = int(i.split("delete_layer")[0])
				if len(field["data"]["layers"]) >= 2 and layer_number != field["data"]["active_layer_number"]:
					field["data"]["layers"].pop(layer_number)
					reload_ui()
					
					if field["data"]["active_layer_number"] + 1 > len(field["data"]["layers"]):
						field["data"]["active_layer_number"] = len(field["data"]["layers"]) - 1

			elif "layer" in i:
				field["data"]["active_layer_number"] = int(i.split("layer")[0])

			if i in current_tools:
				active_tool_number = current_tools.index(i)

			if i == "undo":
				if len(temp_data)>0:
					field["data"] = temp_data[-1]
					temp_data.pop(len(temp_data)-1)
					reload_ui()

			if i == "about":
				about_dialog(settings)

			if i == "settings":
				if settings_dialog(copy.deepcopy(settings)):
					reload_settings()

			if i == "hide_panels":
				is_visible_panels = False
				reload_ui()

			if i == "show_panels":
				is_visible_panels = True
				reload_ui()
			
			if i == "selection_mode":
				area = Area(l=field["data"]["active_layer_number"])
				is_selection_mode = True
				reload_ui()
			
			if i == "move_selected_area":
				field["data"]["layers"] = area.move(field["data"]["layers"])
				reload_ui()

			if i == "copy_selected_area":
				copied_data = area.data
				reload_ui()

			if i == "paste_selected_area":
				area = Area(x=(cursor_pos[0]-field["x"])//scale, y=(cursor_pos[1]-field["y"])//scale, l=field["data"]["active_layer_number"], data=copied_data)
				area.is_move = True
				reload_ui()

			if i == "delete_selected_area":
				field["data"]["layers"] = area.delete(field["data"]["layers"])
				area = Area(l=field["data"]["active_layer_number"])
				reload_ui()
			
			if i == "exit_from_selection_mode":
				is_selection_mode = False
				area = Area(l=field["data"]["active_layer_number"])
				reload_ui()

			break

	for e in event:
		if e.type == pg.MOUSEBUTTONDOWN:
			if e.button==1:
				if not is_click_ui:
					if is_selection_mode:
						if area.is_move:
							field["data"]["layers"] = area.enter_area(field["data"]["layers"])
							area = Area(l=field["data"]["active_layer_number"])
							reload_ui()
						elif area.is_selection:
							area.select_area(field["data"]["layers"], (area.x, area.y), ((cursor_pos[0]-field["x"])//scale, (cursor_pos[1]-field["y"])//scale))
							reload_ui()
						elif len(area.data)>0:
							area = Area(l=field["data"]["active_layer_number"])
							reload_ui()
						elif len(area.data)==0:
							area.x, area.y = (cursor_pos[0]-field["x"])//scale, (cursor_pos[1]-field["y"])//scale
							area.l = field["data"]["active_layer_number"]
							area.is_selection = True
							reload_ui()
			
		if e.type == pg.MOUSEWHEEL:
			try:
				if e.y < 0:
					if field["scale"] // 2 > 1:
						field["x"] += (cursor_pos[0] - field["x"]) // 2
						field["y"] += (cursor_pos[1] - field["y"]) // 2
						field["scale"] //= 2
				else:
					if field["scale"] * 2 != 512:
						field["x"] -= cursor_pos[0] - field["x"]
						field["y"] -= cursor_pos[1] - field["y"]
						field["scale"] *= 2
			except Exception:
				pass
		
		if e.type == pg.KEYDOWN:
			if not is_selection_mode:
				if e.key == pg.K_UP:
					if field["data"]["active_layer_number"] == len(field["data"]["layers"]) - 1:
						field["data"]["active_layer_number"] = 0
					else:
						field["data"]["active_layer_number"] += 1

				if e.key == pg.K_DOWN:
					if field["data"]["active_layer_number"] == 0:
						field["data"]["active_layer_number"] = len(field["data"]["layers"]) - 1
					else:
						field["data"]["active_layer_number"] -= 1

				if e.key == pg.K_RIGHT and elements_ui[current_tools[0]].is_active:
					if active_tool_number == len(current_tools) - 1:
						active_tool_number = 0
					else:
						active_tool_number += 1

				if e.key == pg.K_LEFT and elements_ui[current_tools[0]].is_active:
					if active_tool_number == 0:
						active_tool_number = len(current_tools) - 1
					else:
						active_tool_number -= 1

			if e.key == pg.K_l and pg.key.get_mods() & pg.KMOD_CTRL:
				reload_settings()
			
			if e.key == pg.K_HOME:
				field["x"] = 0; field["y"] = 0
			
			if e.key == pg.K_g and pg.key.get_mods() & pg.KMOD_CTRL:
				is_grid_visible = bool((int(is_grid_visible)+1)%2)

			if e.key == pg.K_g and pg.key.get_mods() & pg.KMOD_SHIFT:
				is_axis_visible = bool((int(is_axis_visible)+1)%2)
	
	if area.is_move:
		area.x, area.y = (cursor_pos[0]-field["x"])//scale, (cursor_pos[1]-field["y"])//scale
	
	try:
		if mouse[0]:
			if not is_selection_mode:
				if not is_click_ui and not process:
					if current_tools[active_tool_number]!="elevator":
						for cell in field["data"]["layers"][field["data"]["active_layer_number"]]:
							if cell[0]==(cursor_pos[0] - field["x"]) // field["scale"] and cell[1]==(cursor_pos[1] - field["y"]) // field["scale"] and cell[2]=="elevator":
								for l in range(len(field["data"]["layers"])):
									field["data"]["layers"] = set_cell(field["data"]["layers"], l, (cursor_pos[0] - field["x"]) // (field["scale"]), (cursor_pos[1] - field["y"]) // (field["scale"]), "eraser") 
						field["data"]["layers"] = set_cell(field["data"]["layers"], field["data"]["active_layer_number"], (cursor_pos[0] - field["x"]) // (field["scale"]), (cursor_pos[1] - field["y"]) // (field["scale"]), current_tools[active_tool_number])
					elif current_tools[active_tool_number]=="elevator":
						for l in range(len(field["data"]["layers"])):
							field["data"]["layers"] = set_cell(field["data"]["layers"], l, (cursor_pos[0] - field["x"]) // (field["scale"]), (cursor_pos[1] - field["y"]) // (field["scale"]), current_tools[active_tool_number])

		if mouse[2]:
			field["x"] += cursor_pos[0] - start_position[0]
			field["y"] += cursor_pos[1] - start_position[1]
		start_position = pg.mouse.get_pos()

	except IndexError:
		pass

"""-----------------------------Main Functions----------------------------------"""

@thread
def field_update():
	global saved_field_coords
	global field
	global fps_field

	clock = pg.time.Clock()

	is_holding = False

	while run:
		if not process or settings["playback_speed"]=="FPS":
			clock.tick(FPS)
			fps_field = int(clock.get_fps())
		elif settings["playback_speed"]!="MAX":
			sleep(int(settings["playback_speed"])/1000)

		if process:
			if isinstance(field["data"]["layers"], list):
				saved_field_coords = [0, 0]
				saved_field_coords[0], saved_field_coords[1], field["data"]["layers"] = to_array(field["data"]["layers"])

			f = cells_update(field["data"]["layers"], names_cells, list_cells_rules)
			if process:
				field["data"]["layers"] = f
				cursor_pos = pg.mouse.get_pos()
				mouse = pg.mouse.get_pressed()
				if mouse[0]:
					try:
						if (cursor_pos[1] - field["y"]) // field["scale"] - saved_field_coords[1]>=0 and (cursor_pos[0] - field["x"]) // field["scale"] - saved_field_coords[0]>=0:
							if field["data"]["layers"][field["data"]["active_layer_number"]][(cursor_pos[1] - field["y"]) // field["scale"] - saved_field_coords[1]][(cursor_pos[0] - field["x"]) // field["scale"] - saved_field_coords[0]] == "button":
								field["data"]["layers"] = set_cell(field["data"]["layers"], field["data"]["active_layer_number"], (cursor_pos[0] - field["x"]) // (field["scale"]) - saved_field_coords[0], (cursor_pos[1] - field["y"]) // (field["scale"]) - saved_field_coords[1], "button active")
							elif field["data"]["layers"][field["data"]["active_layer_number"]][(cursor_pos[1] - field["y"]) // field["scale"] - saved_field_coords[1]][(cursor_pos[0] - field["x"]) // field["scale"] - saved_field_coords[0]] == "manual switch" and not is_holding:
								field["data"]["layers"] = set_cell(field["data"]["layers"], field["data"]["active_layer_number"], (cursor_pos[0] - field["x"]) // (field["scale"]) - saved_field_coords[0], (cursor_pos[1] - field["y"]) // (field["scale"]) - saved_field_coords[1], "manual switch active")
								is_holding = True
							elif field["data"]["layers"][field["data"]["active_layer_number"]][(cursor_pos[1] - field["y"]) // field["scale"] - saved_field_coords[1]][(cursor_pos[0] - field["x"]) // field["scale"] - saved_field_coords[0]] == "manual switch active" and not is_holding:
								field["data"]["layers"] = set_cell(field["data"]["layers"], field["data"]["active_layer_number"], (cursor_pos[0] - field["x"]) // (field["scale"]) - saved_field_coords[0], (cursor_pos[1] - field["y"]) // (field["scale"]) - saved_field_coords[1], "manual switch")
								is_holding = True
					except IndexError:
						pass
				else:
					is_holding = False

		elif not isinstance(field["data"]["layers"], list):
			try:
				field["data"]["layers"] = to_list(field["data"]["layers"], saved_field_coords[0], saved_field_coords[1])
			except Exception:
				pass

@thread
def update():
	global saved_field_coords
	global field
	global fps_update
	global cells_textures
	global area
	global scale

	clock = pg.time.Clock()

	scale = field["scale"]
	cells_textures = get_cells_texture(scale, textures, names_cells)

	while run:
		clock.tick(FPS)

		mouse = pg.mouse.get_pressed()
		cursor_pos = pg.mouse.get_pos()

		screen.fill(settings["background_color"])

		try:
			cells_surface = pg.Surface((screen.get_rect().width, screen.get_rect().height))
			cells_surface.fill(settings["background_color"])

			field_x, field_y = copy.copy(field["x"]), copy.copy(field["y"])

			if scale!=field["scale"]:
				scale = field["scale"]
				cells_textures = get_cells_texture(scale, textures, names_cells)

			try:
				f = copy.deepcopy(field["data"]["layers"][field["data"]["active_layer_number"]])

				if not isinstance(f, list):
					for i in range(np.shape(f)[0]):
						for j in range(np.shape(f)[1]):
							if f[i][j]!="" and field_x + saved_field_coords[0] * (scale) + (j + 1) * (scale) >= 0 and field_x + saved_field_coords[0] * (scale) + j * (scale) < screen.get_width() and field_y + saved_field_coords[1] * (scale) + (i + 1) * (scale) >= 0 and field_y + saved_field_coords[1] * (scale) + i * (scale) < screen.get_height():
								try:
									cells_surface.blit(cells_textures[f[i][j]], (field_x + saved_field_coords[0] * (scale) + j * (scale), field_y + saved_field_coords[1] * (scale) + i * (scale)))
								except KeyError:
									cells_surface.blit(cells_textures["UNKNOWN"], (field_x + saved_field_coords[0] * (scale) + j * (scale), field_y + saved_field_coords[1] * (scale) + i * (scale)))
				else:
					for cell in f:
						if field_x + cell[0] * (scale) < screen.get_rect().width and field_x + cell[0] * (scale) + (scale) >= 0 and field_y + cell[1] * (scale) < screen.get_rect().height and field_y + cell[1] * (scale) + (scale) >= 0:
							try:
								cells_surface.blit(cells_textures[cell[2]], (field_x + cell[0] * (scale), field_y + cell[1] * (scale)))
							except KeyError:
								cells_surface.blit(cells_textures["UNKNOWN"], (field_x + cell[0] * (scale), field_y + cell[1] * (scale)))

				if not process:
					cells_surface.blit(pg.transform.scale(textures["cursor"], (scale, scale)), ((cursor_pos[0] - field_x) // (scale) * scale + field_x, (cursor_pos[1] - field_y) // (scale) * scale + field_y))
					
					if is_grid_visible and scale>=16:
						grid_surface = pg.Surface(cells_surface.get_size(), pg.SRCALPHA)
						
						if settings["grid"]["mode"]=="HORIZONTAL":
							[pg.draw.line(grid_surface, (settings["grid"]["color"][0], settings["grid"]["color"][1], settings["grid"]["color"][2], settings["grid"]["opacity"]), (0, field_y%scale+i*scale), (screen.get_width(), field_y%scale+i*scale)) for i in range(screen.get_height()//scale+1)]
						elif settings["grid"]["mode"]=="VERTICAL":
							[pg.draw.line(grid_surface, (settings["grid"]["color"][0], settings["grid"]["color"][1], settings["grid"]["color"][2], settings["grid"]["opacity"]), (field_x%scale+i*scale, 0), (field_x%scale+i*scale, screen.get_height())) for i in range(screen.get_width()//scale+1)]
						else:
							[pg.draw.line(grid_surface, (settings["grid"]["color"][0], settings["grid"]["color"][1], settings["grid"]["color"][2], settings["grid"]["opacity"]), (0, field_y%scale+i*scale), (screen.get_width(), field_y%scale+i*scale)) for i in range(screen.get_height()//scale+1)]
							[pg.draw.line(grid_surface, (settings["grid"]["color"][0], settings["grid"]["color"][1], settings["grid"]["color"][2], settings["grid"]["opacity"]), (field_x%scale+i*scale, 0), (field_x%scale+i*scale, screen.get_height())) for i in range(screen.get_width()//scale+1)]
						
						cells_surface.blit(grid_surface, (0,0))
					
					if is_axis_visible:
						pg.draw.line(cells_surface, (255, 0, 0), (0, field_y), (screen.get_width(), field_y))
						pg.draw.line(cells_surface, (0, 255, 0), (field_x, 0), (field_x, screen.get_height()))
					
					selected_area = pg.Surface(cells_surface.get_size(), pg.SRCALPHA)
					if area.is_selection:
						min_x, min_y, max_x, max_y = min((cursor_pos[0]-field_x)//scale, area.x), min((cursor_pos[1]-field_y)//scale, area.y), max((cursor_pos[0]-field_x)//scale, area.x), max((cursor_pos[1]-field_y)//scale, area.y)
						width, height = abs(min_x-max_x)+1, abs(min_y-max_y)+1
						pg.draw.rect(selected_area, settings["selected_area_settings"]["color"], (min_x*scale+field_x, min_y*scale+field_y, width*scale, height*scale))
					elif len(area.data)>0 and not area.is_move:
						pg.draw.rect(selected_area, settings["selected_area_settings"]["color"], (area.x*scale+field_x, area.y*scale+field_y, len(area.data[0])*scale, len(area.data)*scale))
					elif len(area.data)>0 and area.is_move:
						pg.draw.rect(selected_area, settings["selected_area_settings"]["color"], (area.x*scale+field_x, area.y*scale+field_y, len(area.data[0])*scale, len(area.data)*scale))
						for i in range(len(area.data)):
							for j in range(len(area.data[0])):
								if area.data[i][j]!="":
									try:
										selected_area.blit(cells_textures[area.data[i][j]], (area.x*scale+field_x+j*scale, area.y*scale+field_y+i*scale))
									except KeyError:
										selected_area.blit(cells_textures["UNKNOWN"], (area.x*scale+field_x+j*scale, area.y*scale+field_y+i*scale))
					
					selected_area.set_alpha(settings["selected_area_settings"]["opacity"])
					cells_surface.blit(selected_area, (0,0))

			except IndexError:
				pass
			
			screen.blit(cells_surface, (0, 0))
		except KeyError:
			pass

		for i in elements_ui:
			try:
				elements_ui[i].update(screen, textures, field, mouse, cursor_pos, current_tools, active_tool_number)
				if elements_ui[i].get_caption(cursor_pos) != "" and settings["is_visible_ui_caption"]:
					ui_caption = font_object.render(elements_ui[i].get_caption(cursor_pos), True, settings["ui_caption_color"])
					ui_caption_rect = ui_caption.get_rect()
					ui_caption_rect.centerx = screen.get_rect().centerx
					screen.blit(ui_caption, ui_caption_rect)
			except Exception:
				pass
		pg.display.update()

		fps_update = int(clock.get_fps())

def main():
	global screen_size
	global screen
	global run
	global elements_ui
	global start_position
	global fps_main
	start_position = pg.mouse.get_pos()
	clock = pg.time.Clock()
	while run:
		clock.tick(FPS)

		event = pg.event.get()

		mouse = pg.mouse.get_pressed()
		cursor_pos = pg.mouse.get_pos()

		control(event, mouse, cursor_pos)

		for e in event:
			if e.type == pg.QUIT:
				if ask_dialog("Exit", "Are you sure?"):
					run = False
			if e.type == pg.VIDEORESIZE:
				screen = pg.display.set_mode((e.w, e.h), pg.RESIZABLE)
				reload_ui()
		
		fps_main = int(clock.get_fps())

		# print(fps_main, fps_update, fps_field)

if __name__=="__main__":
	update()
	field_update()
	main()