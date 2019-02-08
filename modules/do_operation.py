### PERFORM ARTIHMETIC OPERATION WITH RANDOM OPERATORS

def do_operation(value, op):
	try:
		from random import triangular
		m_value = triangular(op[1], op[2]) if (len(op) > 2)	else op[1]

		if (op[0] == "subtract"):
			return (value - m_value)
		elif (op[0] == "add"):
			return (value + m_value)
		elif (op[0] == "multiply"):
			return (value * m_value)
		elif (op[0] == "divide"):
			return (value / m_value)
		elif (op[0] == "random"):
			return (m_value)
		else:
			print(f"WARNING: {op[0]} is an invalid operation.")
			return (m_value)
	except Exception as e:
		return log_error(f"Invalid operation: {e}.")