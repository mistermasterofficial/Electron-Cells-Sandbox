import json
import tkinter
import tkinter.filedialog
import pygame as pg

def open_filedialog():
	top = tkinter.Tk()
	top.iconphoto(True, tkinter.PhotoImage(file="default_textures/icon.png"))
	top.withdraw()
	file_name = tkinter.filedialog.askopenfilename(filetypes=[("Electron Cell Sandbox file","*.ecs")])
	top.destroy()
	return file_name

def open_file(field):
	open_file = open_filedialog()

	caption = ""

	if open_file != "":
		try:
			with open(open_file, "r") as f:
				data = json.load(f)
				for l in range(len(data["layers"])):
					for i in range(len(data["layers"][l])):
						data["layers"][l][i] = tuple(data["layers"][l][i])
			f = {}
			f["data"], f["file_path"] = data, open_file
			caption = open_file

			for l in f["data"]["layers"]:
				for cell in l:
					if isinstance(cell[0], int) and isinstance(cell[1], int) and isinstance(cell[2], str):
						continue
					else:
						print(1 / 0)

			field["data"], field["file_path"] = f["data"], f["file_path"]

		except Exception:
			top = tkinter.Tk()
			top.iconphoto(True, tkinter.PhotoImage(file="default_textures/icon.png"))
			top.withdraw()
			tkinter.messagebox.showerror("Open file error", "The file is not readable!")
			top.destroy()
			caption = ""

	return field, caption

# def open_file_without_filedialog(file_path):
# 	with open(file_path, "r") as f:
# 		data = json.load(f)
# 		for l in range(len(data["layers"])):
# 			for i in range(len(data["layers"][l])):
# 				for j in range(len(data["layers"][l][i])):
# 					data["layers"][l][i][j] = tuple(data["layers"][l][i][j])
# 	field["data"], field["file_path"] = data, file_path
# 	caption = file_path

# 	return field, caption