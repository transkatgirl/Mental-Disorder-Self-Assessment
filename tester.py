import json
import csv
import datetime
import pixie
import math

input_file = open("data/whodas.json")
data = json.loads(input_file.read())

boxes = {}
connections = []
layers = []

def flatten_tree(item, levels, headers):
	box = {}
	if "label" in item:
		box["heading"] = item["label"]
		box["level"] = item["level"]
	elif "header" in item:
		if item["header"] in headers:
			if headers[item["header"]]["show"]:
				box["heading"] = item["header"]
			box["level"] = headers[item["header"]]["level"]
			box["body"] = item["items"]
	if "level" in box:
		while box["level"] >= len(layers):
			layers.append([])

		if "id" in item:
			boxes[item["id"]] = box
			layers[box["level"]].append(item["id"])
	if "members" in item:
		for member in item["members"]:
			if "id" not in member:
				if "header" in member:
					member["id"] = item["id"] + "." + member["header"]
			if "id" in member:
				connections.append({"from": item["id"], "to": member["id"]})
			flatten_tree(member, levels, headers)

scales = {}

def flatten_scales(id, item):
	scale = {}
	if "label" in item:
		scale["label"] = item["label"]
	if "choices" in item:
		scale["choices"] = item["choices"]
	if "scoring" in item:
		scale["scoring"] = item["scoring"]
	scales[id] = scale
	if "subscales" in item:
		for key, value in item["subscales"].items():
			flatten_scales(key, value)

def print_scale_scoring(indent, id, item):
	if "label" in item:
		print(("\t" * indent) + "-", item["label"], "(" + id + ")")
	else:
		print(("\t" * indent) + "-", id)
	if "choices" in item:
		print(("\t" * (indent + 1)) + "- choices:", item["choices"])
	if "scoring" in item:
		for key, value in item["scoring"].items():
			print(("\t" * (indent + 1)) + "-", key + ":", value)

	if "subscales" in item:
		for key, value in item["subscales"].items():
			print_scale_scoring(indent + 1, key, value)



print("Version: " + str(datetime.datetime.fromtimestamp( data["version"] / 1000 )) + "\n")
print(data["metadata"]["label"] + " (" + data["metadata"]["label_short"] + ")\n")
for line in data["metadata"]["description"]:
	print(line)


print("\nReferences:")

for reference in data["metadata"]["references"]:
	print("- " + reference["title"] + "\n\t" + reference["link"] + "\n\tRetrieved " + str(datetime.datetime.fromtimestamp( reference["retrieved"] / 1000 )))

print("\nType: " + data["metadata"]["type"])

if "dependencies" in data["metadata"]:
	print("\nDependencies:")
	for dependency in data["metadata"]["dependencies"]:
		print("- " + dependency["file"] + "\n\tVersion: " + str(datetime.fromtimestamp( dependency["version"] / 1000 )))
		# TODO: Print mappings

if data["metadata"]["type"] == "tree-diagram":
	print("\n--- Tree Diagram ---")
	headers = {}
	i = 0
	for level in data["levels"]:
		show_headers = True
		if "show_headers" in level:
			show_headers = level["show_headers"]
		if "headers" in level:
			for header in level["headers"]:
				headers[header] = {"level": i, "show": show_headers}
		i += 1

	flatten_tree(data["tree"], data["levels"], headers)

	print("\nLevels:")
	for level in data["levels"]:
		print(level)
	print("\nLayers:")
	for layer in layers:
		print(layer)
	print("\nBoxes:")
	for box in boxes.items():
		print(box)
	print("\nConnections:")
	for connection in connections:
		print(connection)


	#print(tree_width)
	#print(tree_height)

	"""image = pixie.Image((tree_width+1) * 250, (tree_height+1) * 250)
	font = pixie.read_font("Roboto-Regular_1.ttf")
	font.size = 20

	for box in boxes.values():
		if "heading" in box:
			image.fill_text(
				font,
				box["heading"],
				bounds = pixie.Vector2(200, 200),
				transform = pixie.translate(box["x"] * 250, box["y"] * 250)
			)

	image.write_file("text.png")"""

	# TODO

if data["metadata"]["type"] == "questionnaire":
	print("\n--- Questionnaire ---\n")
	# TODO

	for key, value in data["scales"].items():
		flatten_scales(key, value)

	for line in data["instructions"]:
		print(line)

	length = 0
	for question_set in data["questions"].values():
		length += len(question_set)

	print("\nThis questionnaire will take approximately", math.ceil(datetime.timedelta(seconds=data["estimated_seconds_per_question"] * length) / datetime.timedelta(minutes=1)), "minutes to complete.")

	for section, question_set in data["questions"].items():
		print("\n#", section + "\n")
		last_instruction = ""
		for question, scale in question_set.items():
			choice = None
			if scale in scales:
				if "choices" in scales[scale]:
					choice = data["choices"][scales[scale]["choices"]]
			elif scale in data["choices"]:
				choice = data["choices"][scale]
			if choice is not None:
				if "instructions" in choice:
					if choice["instructions"] != last_instruction:
						print(choice["instructions"])
						last_instruction = choice["instructions"]
				print("-", question)
				if "options" in choice:
					for option in choice["options"]:
						print("\t-", option)
				if "range" in choice:
					print("\t- Minimum:", choice["range"]["minimum"])
					print("\t- Maximum:", choice["range"]["maximum"])
					print("\t- Increment:", choice["range"]["increment"])

	print("\nScoring:")
	for key, value in data["scales"].items():
		print_scale_scoring(0, key, value)


	# TODO: Decode scoring info


#print()
#print(data)