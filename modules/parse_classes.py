def main(classes):
	from collections import ChainMap
	class_list = {}

	for key, v in classes.items():
		if ("Parents" in v):
			buffer_obj = v
			buffer_obj_props = [];

			if ("properties" in v):
				for vp in v["properties"]:
					buffer_obj_props.append(vp)
			for parent in v["Parents"]:
				if (parent in class_list):
					buffer_obj = (dict(ChainMap(class_list[parent], buffer_obj)))
				if ("properties" in class_list[parent]):
					for vp in class_list[parent]["properties"]:
						buffer_obj_props.append(vp)
			if ("properties" in v):
				buffer_obj["properties"] = buffer_obj_props
			buffer_obj.pop("Parents", None)
			class_list[key] = buffer_obj
		else:
			class_list[key] = v

	return class_list