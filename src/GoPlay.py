import sys


from CaptureGo import CaptureGo


def main():
	n = len(sys.argv)
	if n == 2:
		game = CaptureGo(int(sys.argv[1]))
	elif n == 3:
		game = CaptureGo(int(sys.argv[1]), float(sys.argv[2]))
		print("GOT HERE")
	else:
		game = CaptureGo()

	while(game.has_won() == False):
		game.display()
		command = input(">>> ")
		game.handle_command(command)

if __name__ == "__main__":
	main()