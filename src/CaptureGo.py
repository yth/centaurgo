import numpy as np


from GoBoard import GoBoard

# Required Captures
N = 40 # ~ SIZE * SIZE / 2


class CaptureGo:
	def __init__(self):
		self.board = GoBoard()
		self.mcst = {};

	def has_won(self):
		if self.board.w_captures > N or self.board.b_captures > N:
			return True
		return False

	def display(self):
		print("   0 1 2 3 4 5 6 7 8")
		for i in range(self.board.size):
			print("{}: ".format(i), end='')
			for j in range(self.board.size):
				if self.board.board[i][j] == 1:
					print("x ", end='')
				elif self.board.board[i][j] == -1:
					print("o ", end='')
				else:
					print(". ", end='')
			print()


	def handle_command(self, command):
		if command == "h" or command == "help":
			print("Helpful message")

		elif command == "q" or command == "quit":
			self.board.w_captures = N + 1

		elif command == "r" or command == "recommend":
			... # Run simulation and suggest best move

		elif "p" in command:
			command = command.split()
			if "p" in command[0] and len(command) == 3:
				try:
					x = int(command[1])
				except:
					print("Bad x coordinate")
					return

				try:
					y = int(command[2])
				except:
					print("Bad y coordinate")
					return

				played = self.board.play_move(x, y)

				if played == False:
					print("Bad move, try again")
			else:
				print("Bad move")
