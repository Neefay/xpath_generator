def main(config):

	### MODULE IMPORTS

	import os, string
	import xml.etree.ElementTree as ET

	from os import path
	from string import Template
	from collections import ChainMap

	from modules.helpers import read_json
	from modules.helpers import log_error
	from modules.helpers import log_ok
	from modules.helpers import go_to_folder
	from modules.helpers import create_file
	from modules.helpers import read_template
	from modules.helpers import obj_forbidden
	from modules.helpers import write_line
	from modules.helpers import get_stored_value
	from modules.parse_values import main as parse_values
	from modules.parse_classes import main as parse_classes

	from modules.do_operation import do_operation
	from modules.render_template import render_template

	log_ok("Initializing...")

	### PATH VALUES

	MODULE_PATH = os.path.join(os.path.dirname(__file__))
	HOME_DIR = os.getcwd()

	### PARSE JSON CONFIG FILE

	try:
		config = read_json(config)
	except Exception as e:
		return log_error("Invalid config file.")
	finally:
		log_ok("Valid config file.")

	### STORE ALL GLOBAL VALUES

	try:
		classes = read_json("classes.json")

		stored_values = parse_values(classes["values"])
		stored_classes = parse_classes(classes["classes"])
	except Exception as e:
		return log_error(f"Invalid classes file or error: {e}")

	### SPACING VALUES

	TEMPLATE_LINE = 5
	TAB_SPACE = 3
	NL = "\n"

	### ROOT CONFIG VARIABLES

	try:
		MODS_DIR = config["target_folder"]
		OUTPUT_DIR = config["output_folder"]
		CONFIG_MODS = config["main"]
	except Exception as e:
		return log_error((f"Property: {str(e)} missing from main config."))

	GAME_MODS_DIR = (MODS_DIR + "/")

	try:
		if not os.path.exists(OUTPUT_DIR):
			raise
	except Exception:
		return log_error("Output directory does not exist.")
	finally:
		log_ok("Valid output directory.")

	### MOD CONFIG VARIABLES

	for mod in CONFIG_MODS:
		try:
			mod_folder = mod["folder"]
			mod_defs = mod["defs"]
		except Exception as e:
			return log_error((f"Property: {str(e)} missing from mod config."))
		try:
			folder_name = (mod["label"] if ("label" in mod) else mod_folder)
			current_def_path = (GAME_MODS_DIR + mod_folder + "/Defs/")
		except Exception as e:
			return log_error(e)

		### DEF CONFIG VARIABLES

		for mod_def in mod_defs:
			print("--------------")
			try:
				def_folder = mod_def["folder"]
				def_files = mod_def["files"]
			except Exception as e:
				return log_error((f"Property: {str(e)} missing from def config."))
			try:
				def_path = ("/" + mod_def["path"]) if ("path" in mod_def) else "Defs"
				def_defType = mod_def["defType"] if ("defType" in mod_def) else "ThingDef"
				mod_def_path = (current_def_path + def_folder + "/")
				def_file_exported = {}
			except Exception as e:
				return log_error(e)

			### CREATE BASE FOLDER FOR MOD

			go_to_folder(OUTPUT_DIR, folder_name, HOME_DIR)
			log_ok(f"Mod folder {folder_name} created.")

			### FILE CONFIG VARIABLES

			for def_file in def_files:
				try:
					def_file_defName = def_file["defName"]
					def_file_properties = def_file["properties"]
				except Exception as e:
					return log_error((f"Property: {str(e)} missing from file config."))

				### PARSE CLASS PROPERTIES

				try:
					def_file_Class = def_file["Classes"] if ("Classes" in def_file) else None

					if not (def_file_Class is None):
						cache_properties = []
						for c_class in def_file_Class:
							if (c_class in stored_classes):
								def_file = (dict(ChainMap(stored_classes[c_class], def_file)))
								matching_class = stored_classes[c_class]
								if ("properties" in matching_class):
									for vp in matching_class["properties"]:
										cache_properties.append(vp)
									for vp in def_file_properties:
										cache_properties.append(vp)
									def_file_properties = cache_properties
						def_file.pop("Classes", None)
				except Exception as e:
					return log_error(e)
				print("-----------------")

				### PARSE XML FILE

				try:
					xml_file = (mod_def_path + def_file_defName + ".xml")
					if not os.path.isfile(xml_file):
						raise
				except Exception as e:
					return log_error(f"File {xml_file} does not exist!")
				try:
					tree = ET.parse(xml_file)
					root = tree.getroot()
				except Exception as e:
					return log_error(f"Failed to parse XML file. ({e}).")

				log_ok(f"Read {def_file_defName}.xml.", 2)

				def_file_exported[def_file_defName] = []
				exported_properties = {};

				### CREATE DEF SUB-FOLDER

				go_to_folder(os.path.join(OUTPUT_DIR, folder_name), def_folder, HOME_DIR)

				### ITERATE THROUGH OBJECTS

				for object_def in root.iter(def_defType):
					try:
						obj_defName = object_def.find("defName").text if (object_def.find("defName") is not None) else object_def.get("Name")
					except Exception as e:
						return log_error(e)

					### CHECK IF OBJECT IS INCLUDED/EXCLUDED

					if obj_forbidden(def_file, obj_defName):
						continue

					### OPTIONAL LABEL/DESC VARIABLES

					try:
						obj_label = object_def.find("label").text if (object_def.find("label") is not None) else ""
						obj_defType = def_file["defType"] if ("defType" in def_file) else def_defType
						exported_properties[obj_defName] = { "label": obj_label, "values": [] }
					except Exception as e:
						return log_error(e)

					### LOOP THROUGH OBJECT PROPERTIES

					for def_prop in def_file_properties:
						try:
							def_prop_tree = def_prop["tree"]
							def_prop_property = def_prop["property"]
						except Exception as e:
							return log_error((f"Property: {str(e)} missing from property config."))
						try:
							prop_path = "/".join(def_prop_tree)
						except Exception as e:
							return log_error(e)

						### PROPERTY FILTER FOR INCLUDED/EXCLUDED OBJECTS

						for target_prop in object_def.findall(prop_path):
							if obj_forbidden(def_prop, obj_defName):
								continue

							for final_prop in target_prop.iter(def_prop_property):
								fpt = final_prop.text

								### PERFORM ARITHMETIC OPERATION OR ASSIGN VALUE

								try:
									if ("operation" in def_prop):
										normalized_values = get_stored_value(def_prop["operation"], stored_values)

										fpt = float(fpt) if '.' in fpt else int(fpt)
										fpt = do_operation(fpt, normalized_values)
										fpt = round(fpt, normalized_values[3] if (len(normalized_values) == 4) else 2)
									elif ("value" in def_prop):
										fpt = get_stored_value(def_prop["value"], stored_values)[0]
									else:
										raise
								except Exception as e:
									return log_error(f"Property '{obj_defName}' has no valid value or operation: {e}.")

								### APPEND NEW DICTIONARY INTO LIST

								this_export = {
									"defType": obj_defType,
									"defPath": def_path,
									"defName": obj_defName,
									"propPath": prop_path,
									"mainProp": def_prop_property,
									"finalValue": fpt,
									"taskDesc": def_prop["desc"] if ("desc" in def_prop) else None
								}
								exported_properties[obj_defName]["values"].append(this_export)
				log_ok("Properties processed.", 3)

				### APPEND DEF LIST INTO MOD PROPERTIES

				def_file_exported[def_file_defName].append(exported_properties)

			### LOOP THROUGH MOD PROPERTIES

			log_ok(f"Creating patch files...", 1)

			for attr, sub_mod_def in def_file_exported.items():

				log_ok(f"/{def_folder}:", 2)

				### CREATE OUTPUT FILE AND READ MAIN TEMPLATE

				try:
					output_file = create_file(os.path.join(OUTPUT_DIR, folder_name, def_folder), (attr + ".xml"))
					tpl_template = read_template(HOME_DIR, "main")

					sub_def_file = {}
				except Exception as e:
					return log_error(e)

				### LOOP THROUGH TEMPLATE LINES UNTIL MIDDLE SECTION

				for line_count, main_template_line in enumerate(tpl_template):
					if (line_count == TEMPLATE_LINE):

						### MOD HEADER COMMENT

						try:
							mod_header_dict = {
								"label": ("CONTENT: " + (mod["label"] if "label" in mod else mod_folder)),
								"desc": mod["desc"] if ("desc" in mod) else "",
							}
							for line in read_template(HOME_DIR, "header_long"):
								output_file.write(write_line(render_template("header_long", Template(line), mod_header_dict), 1))
						except Exception as e:
							return log_error(e)

						### DEF HEADER COMMENT

						try:
							sub_def_file = {}
							for s in def_files:
								if (s["defName"] == attr): sub_def_file = s

							if (len(sub_def_file) > 0):
								def_header_dict = {
									"label": ("PATCH: " + ((sub_def_file["label"]) if "label" in sub_def_file else "")),
									"desc": sub_def_file["desc"] if "desc" in sub_def_file else "",
								}
								if ("label" in sub_def_file):
									for line in read_template(HOME_DIR, "header_mid"):
										output_file.write(write_line(render_template("header_long", Template(line), def_header_dict), (TAB_SPACE-1)))
						except Exception as e:
							return log_error(e)

						### LOOP THROUGH DEF OBJECTS

						for prop in sub_mod_def:
							for i, sp_def_file in prop.items():

								### OBJECT LABEL COMMENT

								if (len(sp_def_file["values"]) > 0):
									try:
										labelHeader = sp_def_file["label"] if ("label" in sp_def_file) else i

										for line in read_template(HOME_DIR, "header"):
											output_file.write(write_line(render_template("header", Template(line), { "label": labelHeader }), TAB_SPACE))
									except Exception as e:
										return log_error(e)

									for exp_values in sp_def_file["values"]:

										### TASK DESCRIPTION COMMMENT

										if (exp_values["taskDesc"] is not None):
											try:
												for line in read_template(HOME_DIR, "header"):
													output_file.write(write_line(render_template("header", Template(line), { "label": ("CHANGE: " + exp_values["taskDesc"]) }), TAB_SPACE, 0))
												output_file.write(NL)
											except Exception as e:
												return log_error(e)

										### WRITE REPLACEMENT XPATH OPERATION

										try:
											for line in read_template(HOME_DIR, "li_replace"):
												output_file.write(write_line(render_template("main", Template(line), exp_values), TAB_SPACE, 0))
										except Exception as e:
											return log_error(e)

										output_file.write(NL*2)
					else:
						output_file.write(main_template_line)
				log_ok(f"Created {attr}.", 3)

				### CLOSES FILES

				output_file.close()
				tpl_template.close()

	print()
	log_ok("All tasks executed successfully!")
	True

	### 👍😎