import json
import tkinter
import tkinter.filedialog
import pygame as pg
import copy

def save_filedialog():
	top = tkinter.Tk()
	top.iconphoto(True, tkinter.PhotoImage(file="default_textures/icon.png"))
	top.withdraw()
	file_name = tkinter.filedialog.asksaveasfilename(filetypes=[("Electron Cell Sandbox file","*.ecs")])
	top.destroy()
	return file_name

def save_file(field):
	caption = ""

	if field["file_path"]=="":
		save_file = save_filedialog()
		if save_file != "" and save_file != ():
			if save_file[-4:]!=".ecs":
				save_file+=".ecs"
			with open(save_file, "w") as f:
				data = copy.deepcopy(field["data"])
				data["layers"] = list(data["layers"])
				for l in range(len(data["layers"])):
					data["layers"][l] = list(data["layers"][l])
					for i in range(len(data["layers"][l])):
						data["layers"][l][i] = list(data["layers"][l][i])
				json.dump(data, f)
			caption = save_file
			field["file_path"] = save_file
	else:
		with open(field["file_path"], "w") as f:
			data = copy.deepcopy(field["data"])
			data["layers"] = list(data["layers"])
			for l in range(len(data["layers"])):
				data["layers"][l] = list(data["layers"][l])
				for i in range(len(data["layers"][l])):
					data["layers"][l][i] = list(data["layers"][l][i])
			json.dump(data, f)
		caption = ""

	return field, caption