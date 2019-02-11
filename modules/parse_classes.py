import copy

PARENT_CLASS = "Inherits"
FIXED_PROPERTY_PREFIX = "$_"

def is_ignored_key(key):
	for i, c in enumerate(FIXED_PROPERTY_PREFIX):
		if (key[i] != c):
			return False
	return True

def remove_prefix(v):
	return v.replace(FIXED_PROPERTY_PREFIX, "")

def get_object_parents(obj, class_list):

	buffer_obj = copy.deepcopy(obj)

	for obj_key, obj_attr in obj.items():

		if (obj_key == PARENT_CLASS):
			for p_v in obj_attr:
				if (p_v in class_list):
					for c_key, c_attr in class_list[p_v].items():
						if (type(c_attr) in [list, int, float]):
							if (c_key in buffer_obj):
								if (type(buffer_obj[c_key]) is str):
									buffer_obj[c_key] = [buffer_obj[c_key]]
								if (type(c_attr) is list):
									sur_list = []
									for s_p in c_attr:
										if not (is_ignored_key(s_p)):
											sur_list.append(s_p)
								buffer_obj[c_key] = buffer_obj[c_key] + (c_attr if (type(c_attr) in [int, float]) else sur_list)
							else:
								if (type(c_attr) is list):
									sur_list = []
									for s_p in c_attr:
										if (type(s_p) is str):
											if not (is_ignored_key(s_p)):
												sur_list.append(s_p)
										if (type(s_p) is dict):
											sur_list.append(s_p)
								buffer_obj[c_key] = (c_attr if (type(c_attr) in [int, float]) else sur_list)
						elif (type(c_attr) in [str]):
							if not (c_key in buffer_obj):
								if not (is_ignored_key(c_key)):
									buffer_obj[c_key] = c_attr
						elif (type(c_attr) in [dict]):
							if not (is_ignored_key(c_key)):
								buffer_obj[c_key] = get_object_parents(c_attr, class_list)
		else:
			if (type(obj_attr) is list):
				if (len(obj_attr) > 0):
					list_root = obj_attr[0]
					if (type(list_root) is dict):
						buffer_obj[obj_key] = []
						for s_obj in obj_attr:
							buffer_obj[obj_key].append(get_object_parents(s_obj, class_list))
				else:
					buffer_obj[obj_key] = []
			elif (type(obj_attr) is dict):
				buffer_obj[obj_key] = (get_object_parents(obj_attr, class_list))

	buffer_obj.pop(PARENT_CLASS, None)
	return buffer_obj

def main(classes):
	class_list = {}

	for key, v in classes.items():
		class_list[key] = get_object_parents(v, class_list)

	class_objs_clone = copy.deepcopy(class_list)

	def normalize_output(obj, parent = None):
		for key, attr in obj.items():
			if (is_ignored_key(key)):
				fixed_key = remove_prefix(key)
				class_objs_clone[parent][fixed_key] = attr
				class_objs_clone[parent].pop(key, None)
			if isinstance(attr, dict):
				normalize_output(attr, key)

	normalize_output(class_list)

	return class_objs_clone