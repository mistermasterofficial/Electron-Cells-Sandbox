import json
import pygame as pg
from os.path import exists
from cells import *

def load_settings_and_textures(names_cells):
	texture_files = {
		"icon": "icon.png",
		"about": "ui/button/about.png",
		"cursor": "cells/cursor.png",
		"tool_cursor": "ui/button/tool_cursor.png",
		"layer_cursor": "ui/button/layer_cursor.png",
		"new_file": "ui/button/new_file_button.png",
		"open_file": "ui/button/open_file_button.png",
		"save_file": "ui/button/save_file_button.png",
		"save_as_file": "ui/button/save_as_file_button.png",
		"add_layer": "ui/button/add_layer.png",
		"delete_layer": "ui/button/delete_layer.png",
		"layer": "ui/button/layer.png",
		"play": "ui/button/play.png",
		"pause": "ui/button/pause.png",
		"undo": "ui/button/undo.png",
		"reproduce_one_step": "ui/button/reproduce_one_step.png",
		"show_panels": "ui/button/show_panels.png",
		"hide_panels": "ui/button/hide_panels.png",
		"settings": "ui/button/settings.png",
		"selection_mode":"ui/button/selection_mode.png",
		"move_selected_area":"ui/button/move_selected_area.png",
		"copy_selected_area":"ui/button/copy_selected_area.png",
		"paste_selected_area":"ui/button/paste_selected_area.png",
		"delete_selected_area":"ui/button/delete_selected_area.png",
		"exit_from_selection_mode":"ui/button/exit_from_selection_mode.png"
	}

	for i in names_cells:
		texture_files[i] = f"cells/{i}.png"

	textures = {}

	with open("settings.json") as f:
		settings = json.load(f)

	settings["font_path"] = "default_textures/ui/font.ttf"

	for i in texture_files.keys():
		textures[i] = "default_textures/" + texture_files[i]

	for i in reversed(settings["selected_texture_packs"]):
		if exists("texture_packs/" + i):
			for j in texture_files.keys():
				if exists("texture_packs/" + i + "/" + texture_files[j]):
					textures[j] = "texture_packs/" + i + "/" + texture_files[j]
			if exists("texture_packs/" + i + "/ui/font.ttf"):
				settings["font_path"] = "texture_packs/" + i + "/ui/font.ttf"

	for i in textures.keys():
		try:
			textures[i] = pg.image.load(textures[i])
		except Exception:
			textures[i] = pg.image.load(textures["UNKNOWN"])
	
	return settings, textures

def get_cells_texture(scale, textures, names_cells):
	cells_textures = {}
	for img in textures:
		try:
			if img in names_cells:
				cells_textures[img] = pg.transform.scale(textures[img], (scale, scale))
		except KeyError:
			continue
	return cells_textures

def reset_settings():
	with open("settings.json", "w") as f:
		f.write('{"selected_area_settings":{"color": [255, 255, 255], "opacity": 127}, "grid": {"mode": "CELL", "color": [255, 255, 255], "opacity": 127}, "is_visible_ui_caption": true, "playback_speed": "FPS", "selected_texture_packs": [], "scale_ui_button": 64, "ui_caption_color": [255, 255, 255], "background_color": [64, 64, 64], "button_active_color": {"opacity": 50, "on_cursor": [255, 255, 255], "on_press": [0, 0, 0]}, "font_path": "default_textures/ui/font.ttf"}')

	with open("cells_data.json", "w") as f:
		f.write('''{
	"cells": {
		"1 electron wire": [
			{
				"range": [
					1
				],
				"searchable": "input wire head",
				"turn into": "1 electron wire head"
			}
		],
		"1 electron wire head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "1 electron wire tail"
			}
		],
		"1 electron wire tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "1 electron wire"
			}
		],
		"2 electron wire": [
			{
				"range": [
					2
				],
				"searchable": "input wire head",
				"turn into": "2 electron wire head"
			}
		],
		"2 electron wire head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "2 electron wire tail"
			}
		],
		"2 electron wire tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "2 electron wire"
			}
		],
		"UNKNOWN": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "UNKNOWN"
			}
		],
		"button": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "button"
			}
		],
		"button active": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "button"
			}
		],
		"comment": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "comment"
			}
		],
		"electron head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "electron tail"
			}
		],
		"electron tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "wire"
			}
		],
		"elevator": [
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "elevator head"
			}
		],
		"elevator head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "elevator tail"
			}
		],
		"elevator tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "elevator"
			}
		],
		"eraser": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "eraser"
			}
		],
		"input wire": [
			{
				"range": [
					1,
					2
				],
				"searchable": "electron head",
				"turn into": "input wire head"
			}
		],
		"input wire head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "input wire tail"
			}
		],
		"input wire tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "input wire"
			}
		],
		"manual switch": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "manual switch"
			}
		],
		"manual switch active": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "manual switch active"
			}
		],
		"output wire": [
			{
				"range": [
					1,
					2
				],
				"searchable": "2 electron wire head",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "1 electron wire head",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "elevator head",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "button active",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "manual switch active",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "output wire head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "switch head",
				"turn into": "output wire head"
			}
		],
		"output wire head": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "output wire tail"
			}
		],
		"output wire tail": [
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "output wire"
			}
		],
		"switch head": [
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "switch off"
			},
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "switch tail"
			}
		],
		"switch off": [
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "switch on"
			}
		],
		"switch on": [
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "switch off"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "electron head",
				"turn into": "switch head"
			}
		],
		"switch tail": [
			{
				"range": [
					1,
					2
				],
				"searchable": "input wire head",
				"turn into": "switch off"
			},
			{
				"range": [
					0
				],
				"searchable": "",
				"turn into": "switch on"
			}
		],
		"wire": [
			{
				"range": [
					1,
					2
				],
				"searchable": "electron head",
				"turn into": "electron head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "output wire head",
				"turn into": "electron head"
			},
			{
				"range": [
					1,
					2
				],
				"searchable": "switch head",
				"turn into": "electron head"
			}
		]
	},
	"current_tools": [
		"eraser",
		"wire",
		"electron head",
		"electron tail",
		"2 electron wire",
		"1 electron wire",
		"elevator",
		"button",
		"manual switch",
		"switch on",
		"switch off",
		"input wire",
		"output wire",
		"comment"
	],
	"modifications": {},
	"output_cells": [],
	"tools": [
		"eraser",
		"wire",
		"electron head",
		"electron tail",
		"2 electron wire",
		"1 electron wire",
		"elevator",
		"button",
		"manual switch",
		"switch on",
		"switch off",
		"input wire",
		"output wire",
		"comment"
	]
}''')

try:
	settings, textures = load_settings_and_textures(names_cells)
except Exception:
	reset_settings()
	names_cells, list_cells_rules, current_tools = cells_load()
	settings, textures = load_settings_and_textures(names_cells)