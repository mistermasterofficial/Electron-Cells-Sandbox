import json

def install_modifications(filename):
	if filename!="":
		with open(filename, "r") as f:
			mod_info = json.load(f)

		with open("cells_data.json", "r") as f:
			data = json.load(f)

			if mod_info["name"] in data["modifications"]:
				return False, ""

		with open("cells_data.json", "w") as f:
			data["modifications"][mod_info["name"]] = []

			for i in mod_info["cells"]:
				if not i in data["cells"].keys():
					data["modifications"][mod_info["name"]].append(i)
					data["cells"][i] = mod_info["cells"][i]

			data["tools"].extend(mod_info["tools"])

			if len(mod_info["output_cells"])>0:
				for cell in mod_info["output_cells"]:
					data["cells"]["output wire"].append({"range":[1,2], "searchable":cell, "turn into":"output wire head"})
				data["output_cells"].extend(mod_info["output_cells"])

			json.dump(data, f, sort_keys=True, indent=4)
		
		return True, mod_info["name"]
	return False, ""

def uninstall_modifications(name):
	with open("cells_data.json", "r") as f:
		data = json.load(f)

		if not name in data["modifications"]:
			print(1)
			return

	with open("cells_data.json", "w") as f:
		for i in data["modifications"][name]:
			try:
				data["current_tools"].remove(i)
			except ValueError:
				pass

			try:
				data["tools"].remove(i)
			except ValueError:
				pass

			try:
				data["cells"]["output wire"].remove({"range":[1,2], "searchable":i, "turn into":"output wire head"})
			except ValueError:
				pass

			try:
				data["output_cells"].remove(i)
			except ValueError:
				pass

			data["cells"].pop(i)

		data["modifications"].pop(name)

		json.dump(data, f, sort_keys=True, indent=4)