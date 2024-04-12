import json
import csv
import datetime
import math

input_file = open("data/hitop.json")
data = json.loads(input_file.read())

layers = []

def flatten_tree(item, depth):
	box = {}
	if "children" in item:
		box["children"] = item["children"]
	if "id" in item:
		box["id"] = item["id"]
	if "label" in item:
		box["heading"] = item["label"]
	elif "header" in item:
		box["heading"] = item["header"]
	if "items" in item:
		box["body"] = item["items"]
	while depth >= len(layers):
		layers.append([])

	if "id" in item:
		has_item = False
		for neighbor in layers[depth]:
			if "id" in neighbor:
				if neighbor["id"] == item["id"]:
					neighbor["children"] += item["children"]
					has_item = True
		if not has_item:
			layers[depth].append(box)
	elif "heading" in box:
		layers[depth].append(box)
	elif "body" in box:
		layers[depth].append(box)

	if "members" in item:
		for member in item["members"]:
			member["children"] = []
			if "id" in item:
				member["children"].append(item["id"])
			else:
				member["children"] += item["children"]
			flatten_tree(member, depth + 1)

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
		print(("\t" * indent) + "-", "(" + id + ")")
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

if "dependencies" in data["metadata"]:
	print("\nDependencies:")
	for dependency in data["metadata"]["dependencies"]:
		print("- " + dependency["file"] + "\n\tVersion: " + str(datetime.datetime.fromtimestamp( dependency["version"] / 1000 )))
		# TODO: Print mappings

if data["metadata"]["type"] == "tree-diagram":
	print("\n--- Tree Diagram ---\n")
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

	flatten_tree(data["tree"], 0)

	level = 0
	for layer in layers:
		if "label" in data["levels"][level]:
			print("-", data["levels"][level]["label"])
		else:
			print("~")
		if "description" in data["levels"][level]:
			print("\t-", data["levels"][level]["description"])
		if len(layer) == 0:
			if "label_long" in data["levels"][level]:
				print("\t-", "[", data["levels"][level]["label_long"], "]")
		level += 1
		for item in layer:
			if "id" in item:
				if "children" in item:
					print("\t-", item["children"], "->", item["id"])
				else:
					print("\t-", item["id"])
				if "heading" in item:
					print("\t\t-", item["heading"])
				if "body" in item:
					for line in item["body"]:
						print("\t\t-", line)
			else:
				if "children" in item:
					print("\t-", item["children"], "->", end=' ')
				else:
					print("\t-", end=' ')
				if "heading" in item:
					print(item["heading"])
					if "body" in item:
						for line in item["body"]:
							print("\t\t-", line)
				elif "body" in item:
						print(item["body"])
				else:
					print()

elif data["metadata"]["type"] == "questionnaire":
	print("\n--- Questionnaire ---\n")

	for key, value in data["scales"].items():
		flatten_scales(key, value)

	for line in data["instructions"]:
		print(line)

	length = 0
	for question_set in data["questions"].values():
		length += len(question_set)

	print("\nThis questionnaire will take approximately", math.ceil(datetime.timedelta(seconds=data["estimated_seconds_per_question"] * length) / datetime.timedelta(minutes=1)), "minutes to complete.")

	if "randomize" in data:
		if data["randomize"]:
			print("\nSection headings will not be displayed in the questionnaire, and the order of questions will be randomized.")

	print()
	for section, question_set in data["questions"].items():
		print("\n#", section + "\n")
		last_instruction = ""
		for question, scale in question_set.items():
			choice = None
			scale_id = None
			if scale in scales:
				scale_id = scale
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
				if scale_id is not None:
					print("\n\t- Scale:", scale_id)

	print("\n")
	for line in data["interpretation"]:
		print(line)

	print("\nScoring:")
	for key, value in data["scales"].items():
		print_scale_scoring(0, key, value)

else:
	print("\nType: " + data["metadata"]["type"])