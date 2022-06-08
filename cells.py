import copy
import json
import numpy as np

def create_field():
	temp = {
		"x":0,
		"y":0,
		"scale":16,
		"file_path":"",
		"data":{
			"active_layer_number":0,
			"layers":[[]]
		}
	}

	return temp

active_tool_number = 0

class Area():
	def __init__(self, x=0, y=0, l=0, data=[]):
		self.x = x
		self.y = y
		self.l = l
		self.data = data

		self.is_move = False
		self.is_selection = False
	
	def select_area(self, field, start_coords, end_coords):
		min_x, min_y, max_x, max_y, width, height = min(start_coords[0], end_coords[0]), min(start_coords[1], end_coords[1]), max(start_coords[0], end_coords[0]), max(start_coords[1], end_coords[1]), abs(min(start_coords[0], end_coords[0])-max(start_coords[0], end_coords[0]))+1, abs(min(start_coords[1], end_coords[1])-max(start_coords[1], end_coords[1]))+1

		self.data = [["" for _ in range(width)] for _ in range(height)]

		for c in field[self.l]:
			if c[0]>=min_x and c[0]<=max_x and c[1]>=min_y and c[1]<=max_y and not c[2] in ["elevator", "elevator head", "elevator tail"]:
				self.data[c[1]-min_y][c[0]-min_x] = c[2]
		
		self.x = min_x
		self.y = min_y
		self.is_selection = False
	
	def enter_area(self, field):
		for i in range(len(self.data)):
			for j in range(len(self.data[0])):
				if self.data[i][j]!="":
					is_not_elevator = True

					for c in field[self.l]:
						if c[0]==self.x+j and c[1]==self.y+i and c[2] in ["elevator", "elevator head", "elevator tail"]:
							is_not_elevator = False
							break
					
					if is_not_elevator:
						field = set_cell(field, self.l, self.x+j, self.y+i, self.data[i][j])
		return field

	def move(self, field):
		for i in range(len(self.data)):
			for j in range(len(self.data[0])):
				is_not_elevator = True

				for c in field[self.l]:
					if c[0]==self.x+j and c[1]==self.y+i and c[2] in ["elevator", "elevator head", "elevator tail"]:
						is_not_elevator = False
						break
				
				if is_not_elevator:
					field = set_cell(field, self.l, self.x+j, self.y+i, "eraser")
		self.is_move = True
		return field
	
	def delete(self, field):
		self.data = [["eraser" for _ in range(len(self.data[0]))] for _ in range(len(self.data))]
		return self.enter_area(field)

def to_array(lis):
	x_list = []
	y_list = []
	view_list = []

	x_lists = [[cell[0] for cell in lis[l]] for l in range(len(lis))]
	y_lists = [[cell[1] for cell in lis[l]] for l in range(len(lis))]
	view_lists = [[cell[2] for cell in lis[l]] for l in range(len(lis))]

	for i in range(len(x_lists)):
		x_list.extend(x_lists[i])
		y_list.extend(y_lists[i])
		view_list.extend(view_lists[i])

	try:
		x, y, width, height = min(x_list), min(y_list), abs(min(x_list)-max(x_list))+1, abs(min(y_list)-max(y_list))+1
	except ValueError:
		x, y, width, height = 0, 0, 1, 1

	array = [[["" for _ in range(width)] for _ in range(height)] for _ in range(len(lis))]

	for l in range(len(lis)):
		for cell in lis[l]:
			array[l][cell[1]-y][cell[0]-x] = cell[2]

	array = np.array(array, dtype="U32")

	return x, y, array

def to_list(array, x_coord, y_coord):
	lis = []

	for l in range(np.shape(array)[0]):
		lis.append([])
		for y in range(np.shape(array)[1]):
			for x in range(np.shape(array)[2]):
				if array[l][y][x]!="":
					lis[l].append((x+x_coord, y+y_coord, array[l][y][x]))

	return lis

def cells_load():
	try:
		with open("cells_data.json", "r") as f:
			cells = json.load(f)
			current_tools_from_file = copy.deepcopy(cells["current_tools"])
			all_tools = copy.deepcopy(cells["tools"])
			mods = copy.deepcopy(cells["modifications"])
			cells = cells["cells"]

		current_tools = []

		if len(current_tools_from_file)==0:
			current_tools = ["eraser"]
		else:
			for t in current_tools_from_file:
				if not t in all_tools and not t in list(mods.values()):
					pass
				elif t in all_tools:
					current_tools.append(t)

		if len(current_tools)==0:
			current_tools = ["eraser"]

		names_cells = [c for c in cells]
		list_cells_rules = [[[rule["searchable"], rule["range"], rule["turn into"]] for rule in cells[name]] for name in names_cells]

		names_cells = tuple(names_cells)

		for c in range(len(list_cells_rules)):
			for r in range(len(list_cells_rules[c])):
				list_cells_rules[c][r][1] = tuple(list_cells_rules[c][r][1])
				list_cells_rules[c][r] = tuple(list_cells_rules[c][r])
			list_cells_rules[c] = tuple(list_cells_rules[c])
		list_cells_rules = tuple(list_cells_rules)

		return names_cells, list_cells_rules, current_tools
	except Exception:
		return None, None, None

names_cells, list_cells_rules, current_tools = cells_load()

def set_cell(field, l, x, y, view):
	if isinstance(field, list):
		if view=="eraser":
			for i in range(len(field[l])):
				if field[l][i][0]==x and field[l][i][1]==y:
					field[l].pop(i)
					return field
		else:
			if (x, y, view) in field[l]:
				return field

			for i in range(len(field[l])):
				if field[l][i][0]==x and field[l][i][1]==y:
					field[l].pop(i)
					break

			field[l].append((x, y, view))
	else:
		if view=="eraser":
			field[l][y][x] = ""
		else:
			field[l][y][x] = view

	return field

def check_cell(field, x1, y1, view):
	cells_number = 0

	for y in range(3):
		for x in range(3):
			if (x!=1 or y!=1) and x1 - 1 + x < np.shape(field)[1] and x1 - 1 + x >= 0 and y1 - 1 + y < np.shape(field)[0] and y1 - 1 + y >= 0 and field[y1 - 1 + y][x1 - 1 + x]==view:
				cells_number += 1

	return cells_number

def cells_update(field, names_cells, list_cells_rules):
	next_field = copy.deepcopy(field)

	for l in range(np.shape(field)[0]):
		for y in range(np.shape(field)[1]):
			for x in range(np.shape(field)[2]):
				cell = field[l][y][x]
				if cell!="elevator" and cell!="comment":
					try:
						for c in list_cells_rules[names_cells.index(cell)]:
							if c[0] == "":
								next_field[l][y][x] = c[2]
								break
							else:
								break_loop = False
								for c1 in c[1]: 
									if check_cell(field[l], x, y, c[0])==c1:
										next_field[l][y][x] = c[2]
										break_loop = True
										break
								if break_loop:
									break
					except ValueError:
						pass 
				elif cell!="comment":
					for c in list_cells_rules[names_cells.index("elevator")]:
						break_loop = False
						for c1 in c[1]:
							if check_cell(field[l], x, y, c[0])==c1:
								for i in range(np.shape(field)[0]):
									next_field[i][y][x] = "elevator head"
								break_loop = True
								break
						if break_loop:
							break

	return next_field
