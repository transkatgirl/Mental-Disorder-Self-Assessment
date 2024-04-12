import csv
import json

scales = {}

id_by_scale = {}
id_by_subscale = {}

with open('testing/HiTOP-SR Alphabetical-Table 1.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		item = {}
		if row[0].strip():
			item["scale"] = row[0].strip()
		if row[1].strip():
			item["subscale"] = row[1].strip()
		if row[4].strip().isdigit():
			item["items"] = int(row[4].strip())
		elif row[2].strip().isdigit():
			item["items"] = int(row[2].strip())
		if row[0] != "Scale" and row[1] != "Subscale" and row[6] != "variable name":
			scales[row[6].strip()] = item
			if "subscale" in item:
				id_by_subscale[item["subscale"]] = row[6].strip()
			elif "scale" in item:
				id_by_scale[item["scale"]] = row[6].strip()

with open('testing/Descriptives prolific final-Table 1.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		#if row[0].strip() not in scales:
		#	print(row[0].strip())
		if row[0].strip() in scales:
			scales[row[0].strip()]["mean"] = row[2]
			scales[row[0].strip()]["stddev"] = row[3]
			scales[row[0].strip()]["min"] = row[4]
			scales[row[0].strip()]["min"] = row[5]

with open('testing/HiTOP-SR Rationally Organized-Table 1.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		#if row[2].strip() not in id_by_scale:
		#	if row[3].strip() not in id_by_subscale:
		#		print(row)
		id = None
		if row[3].strip() in id_by_subscale:
			id = id_by_subscale[row[3].strip()]
		elif row[2].strip() in id_by_scale:
			id = id_by_scale[row[2].strip()]

		if id is not None:
			if row[0].strip():
				if row[0].strip() != "--":
					scales[id]["spectra"] = row[0].strip()
			if row[1].strip():
				if row[1].strip() != "--":
					scales[id]["subfactor"] = row[1].strip()
			if row[6].strip().isdigit():
				if int(row[6].strip()) != scales[id]["items"]:
					print(row)
			elif row[4].strip().isdigit():
				if int(row[4].strip()) != scales[id]["items"]:
					print(row)



with open('testing/HiTOP-SR items by scale-Table 1.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		id = None
		if row[1].strip() in id_by_subscale:
			id = id_by_subscale[row[1].strip()]
		elif row[0].strip() in id_by_scale:
			id = id_by_scale[row[0].strip()]
		#if id is None:
		#	print(row)
		if id is not None:
			if "questions" not in scales[id]:
				scales[id]["questions"] = []
			scales[id]["questions"].append(row[4].strip())
			if row[0].strip():
				if "scale" not in scales[id]:
					scales[id]["scale"] = row[0].strip()
				elif row[0].strip() != scales[id]["scale"]:
					print(row)
			if row[1].strip():
				if "subscale" not in scales[id]:
					print(row)
				elif row[1].strip() != scales[id]["subscale"]:
					print(row)

for key, value in scales.items():
	if "questions" not in value:
		if "subscale" in value:
			print(value)

for key, value in scales.items():
	if "questions" in value:
		if len(value["questions"]) != value["items"]:
			print(value)

#for key, value in scales.items():
#	print("-", key)
#	for key, value in value.items():
#		if key == "questions":
#			print("\t- questions:")
#			for item in value:
#				print("\t\t-", item)
#		else:
#			print("\t-", key + ":", value)

json_scales = {}

for key, value in scales.items():
	if "subscale" not in value:
		item = {"label": value["scale"], "choices": "12-month-significance", "scoring": {"average": True, "percentile": {"function": "normal", "mean": value["mean"], "stddev": value["stddev"]}}, "subscales": {}}
		json_scales[key] = item

for key, value in scales.items():
	if "subscale" in value:
		item = {"label": value["subscale"], "choices": "12-month-significance", "scoring": {"average": True, "percentile": {"function": "normal", "mean": value["mean"], "stddev": value["stddev"]}}}
		json_scales[id_by_scale[value["scale"]]]["subscales"][key] = item

#for scale in json_scales.values():
#	print(scale)

json_questions = {}

for key, value in scales.items():
	if "questions" in value:
		for question in value["questions"]:
			if "subfactor" in value:
				if value["subfactor"] not in json_questions:
					json_questions[value["subfactor"]] = {}
				json_questions[value["subfactor"]][question] = key
			elif "spectra" in value:
				if value["spectra"] not in json_questions:
					json_questions[value["spectra"]] = {}
				json_questions[value["spectra"]][question] = key

print(json.dumps(json_questions))

#for key, value in json_questions.items():
#	print("-", key)
#	for key, value in value.items():
#		print("\t-", key, "\t(" + value + ")")

#for key, value in scales.items():
#	if "subscale" in value:
#		if "scale" not in value:
#			print(value)