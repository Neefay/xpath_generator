### RENDER TEMPLATES WITH PROPER VARIABLES

def render_template(t, s, d):
	try:
		if t not in ["main", "header", "header_long"]:
			raise
	except Exception:
		return log_error(f"Invalid template '{t}'.")

	try:
		if (t == "main"):
			return s.substitute(valuesList=d["valuesList"], defProcedure=d["defProcedure"], defPath=d["defPath"], defType=d["defType"], defName=d["defName"], propPath=d["propPath"], mainProp=d["mainProp"], finalValue=d["finalValue"]);
		if (t == "header"):
			return s.substitute(label=d["label"])
		if (t == "header_long"):
			return s.substitute(label=d["label"], desc=d["desc"])
	except Exception as e:
		return log_error(e)