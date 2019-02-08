import random
from random import triangular
from modules.do_operation import do_operation

straight_types = [int, float]

def get_deep_value(arg_v, stored):
	### Select random value from list
	if (type(arg_v) is list):
		arg_v = random.choice(arg_v)



	### Cross-reference value
	if (type(arg_v) is str):
		if (arg_v[0] is "*"):
			arg_v = arg_v.replace("*", "")
			if (arg_v in stored.keys()):
				arg_v = stored[arg_v]
			else:
				return False

	return arg_v

def main(values, stored_values = {}):
	unsolved_cross_ref = False

	for key, v in values.items():

		### Skip if already processed
		if (key in stored_values):
			continue

		### Store ints and floats right away
		if (type(v) in straight_types):
			stored_values[key] = v
			continue

		### If array, check what's inside
		elif (type(v) is list):

			### Utilizes an operation procedure
			if (type(v[1]) is list):
				current_v = get_deep_value(v[0], stored_values)

				### Unresolved reference
				if (current_v is False):
					unsolved_cross_ref = True
				else:
					current_op = []

					### Handles all random values
					for i, op in enumerate(v[1]):
						current_op.append(get_deep_value(op, stored_values) if (i > 0) else op)

					### Stores calculated value
					dec_points = 0 if (len(v[1]) <= 3) else v[1][3]
					stored_values[key] = round(do_operation(current_v, current_op), dec_points)
					if (dec_points == 0):
						stored_values[key] = int(stored_values[key])

			### Straight value check
			else:
				v_cache = []

				for i, vl in enumerate(v):

					### Only use the first two numbers
					if ((i+1) > 2):
						continue

					v_value = get_deep_value(vl, stored_values)

					if (v_value is False):
						unsolved_cross_ref = True
						v_cache = []
						break
					else:
						v_cache.append(v_value)

				### Choose random floating value with proper decimal points
				if (len(v_cache) > 0):
					dec_points = 0 if (len(v) <= 2) else v[2]
					stored_values[key] = round(triangular(v_cache[0], v_cache[1]), dec_points)
					if (dec_points == 0):
						stored_values[key] = int(stored_values[key])

		### Cross-reference value
		elif (type(v) is str):
			if (v[0] is "*"):
				v = v.replace("*", "")

				if (v in stored_values.keys()):
					stored_values[key] = stored_values[v]
				else:
					unsolved_cross_ref = True
			else:
				stored_values[key] = v

	### Recursion loop
	if (unsolved_cross_ref):
		return main(values, stored_values)
	else:
		return stored_values