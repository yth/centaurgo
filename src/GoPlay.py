from CaptureGo import CaptureGo


def main():
	game = CaptureGo()
	while(game.has_won() == False):
		game.display()
		command = input(">>> ")
		game.handle_command(command)

if __name__ == "__main__":
	main()