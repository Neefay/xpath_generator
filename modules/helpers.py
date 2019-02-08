import os
from os import path

def read_json(file):
	import json
	with open(file) as f:
		return json.load(f)

def log_error(e):
	print(f"ERROR: {e}")
	print("ABORTING.\n")
	return False

def log_ok(m,t = 0):
	t = ("\t"*t)
	print(f"OK:{t} {m}")

def go_to_folder(out, folder, home):
	try:
		os.chdir(out)
		if not os.path.exists(folder):
			os.makedirs(folder)
		os.chdir(folder)
		if home:
			os.chdir(home)
	except Exception as e:
		log_error(e)

def create_file(path, name):
	try:
		os.chdir(path)
		return open(name, "w")
	except Exception as e:
		return log_error(e)

def read_template(home, t):
	try:
		o_path = os.getcwd()
		os.chdir(os.path.join(home, "templates"))
		handle = open((f"tpl_{t}.xml"), "r")
	except Exception as e:
		return log_error(e)
	os.chdir(o_path)
	return handle

def obj_forbidden(props, obj):
	if ("include" in props):
		if not ((obj in props["include"])):
			return True
	if ("exclude" in props):
		if (obj in props["exclude"]):
			return True
	return False

def get_stored_value(values, stored):
	op_cache = []
	if not (type(values) is list):
		values = [values]
	for op in values:
		if (type(op) is str):
			normalized_op = op.replace("*", "")
			if ((normalized_op in stored) and ((op[0] == "*"))):
				op_cache.append(stored[normalized_op])
			else:
				op_cache.append(op)
		else:
			op_cache.append(op)
	return op_cache

def write_line(string, tabs = 0, nl = 1):
	return (("\t" * tabs) + string + ("\n" * (0 if (nl is 0) else (nl+1))))