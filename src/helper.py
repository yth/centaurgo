# Parse the command of type a string and 2 ints
def parse_command_coordinate(command):
	command = command.split()
	if len(command) == 3:
		try:
			x = int(command[1])
			command[1] = x
		except:
			print("Bad x coordinate")
			return None

		try:
			y = int(command[2])
			command[2] = y
		except:
			print("Bad y coordinate")
			return None

		return command

