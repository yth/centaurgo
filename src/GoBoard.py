# Possible board intersection states
# Also used as Enums
WHITE_KO, WHITE, EMPTY, BLACK, BLACK_KO = range(-2,3)


7# Using OGS Standard 9x9 Komi
KOMI = 5.5


# Only 9x9 Capture Go is considered
SIZE = 9


import numpy as np
import copy


""" TODO: Define the game board as:
  1 2 3 ...
A 0 1 2 ...
B s s+1 ...
C 2s 2s+1 ...
. .
. .
. .
where s is the size of the board, and 0, 1 2 ... s ... 2s ... are the indexes.
"""


class GoBoard:
	def __init__(self, board = None,
				 size = SIZE, komi = KOMI,
				 white_captures = 0, black_captures = 0):

		# Check if coords and moves are doing the same thing
		if board == None:
			# Board State and Board State Helpers
			self.board = np.zeros([size, size])
			self.size = size
			# Idea borrowed from MuGo by Brian Lee (brilee)
			self.moves = [(i, j) for i in range(size) for j in range(size)]
			self.neighbors = {(x, y): list(filter(self.check_bounds, [(x+1, y), (x-1, y), (x, y+1), (x, y-1)])) for (x, y) in self.moves}

			# Capture State
			self.w_captures = white_captures + komi
			self.b_captures = black_captures

			# Current Player
			self.current_player = BLACK
		else: # Copy the passed in board if it is not None
			# Board State and Board State Helpers
			self.board = copy.deepcopy(board.board)
			self.size = board.size
			self.neighbors = copy.deepcopy(board.neighbors)
			self.moves = copy.deepcopy(board.moves)

			# Capture State
			self.w_captures = board.w_captures
			self.b_captures = board.b_captures

			# Current Player
			self.current_player = board.current_player


	# Idea borrowed from MuGo by Brian Lee (brilee)
	def check_bounds(self, c):
		return c[0] % self.size == c[0] and c[1] % self.size == c[1]


	# Place a marker for any value at the coord x, y
	# Only used for setting up testing conditions.
	# For anything else, use play_move instead.
	def place_marker(self, marker, x, y):
		self.board[x][y] = marker


	# Create a list of liberties for the group with a stone at x, y.
	# Does not work if the value at x, y on board is not BLACK or WHITE
	def list_liberties(self, x, y):
		color = self.board[x][y]

		frontier = [(x, y)]
		explored = {}
		liberties = []
		while frontier:
			x, y = frontier.pop()
			if self.board[x][y] == EMPTY or \
				self.board[x][y] == WHITE_KO or \
				self.board[x][y] == BLACK_KO:
				liberties.append((x, y))
			else:
				explored[(x, y)] = True
				for x, y in self.neighbors[(x, y)]:
					if self.board[x][y] != color * -1 and \
					 	(x, y) not in explored:
						frontier.append((x, y))

		return liberties


	# Captures the group with a stone at x, y and return the # of captures
	def captures(self, x, y):
		if self.board[x][y] == -self.current_player:
			frontier = [(x, y)]
			explored = {}
			prisoners = 0
			while frontier:
				xp, yp = frontier.pop()
				self.board[xp][yp] = 0
				self.moves.append((xp, yp))
				prisoners += 1
				for xpp, ypp in self.neighbors[(xp, yp)]:
					if (xpp, ypp) not in explored and \
						self.board[xpp][ypp] == -self.current_player:
						frontier.append((xpp, ypp))

			return prisoners
		else:
			return 0


	def play_move(self, x, y):
		if x < 0 or x >= self.size:
			return False
		elif y < 0 or y >= self.size:
			return False
		elif self.board[x][y] == BLACK or self.board[x][y] == WHITE:
			return False
		elif self.board[x][y] == BLACK_KO and self.current_player == BLACK:
			return False
		elif self.board[x][y] == WHITE_KO and self.current_player == WHITE:
			return False

		before = self.board[x][y]
		self.board[x][y] = self.current_player
		playable = False

		# Check if able to capture
		for xp, yp in self.neighbors[(x, y)]:
			if self.board[xp][yp] == -self.current_player:
				liberties = self.list_liberties(xp, yp)
				if len(liberties) == 0:
					playable = True
					captures = self.captures(xp, yp)

					if captures == 1:
						self.board[xp][yp] = -self.current_player * 2

					if self.current_player == WHITE:
						self.w_captures += captures
					else:
						self.b_captures += captures

		# If not capturing, has liberties to live
		if playable == False:
			liberties = self.list_liberties(x, y)
			if liberties:
				playable = True

		if playable:
			# Remove Ko
			for xp in range(self.size):
				for yp in range(self.size):
					if self.board[xp][yp] == self.current_player * 2:
						self.board[xp][yp] = 0

			# Change player
			self.current_player *= -1

			# Remove x, y from moves list
			for i in range(len(self.moves)):
				if self.moves[i] == (x, y):
					del(self.moves[i])
					break

			return True
		else:
			# Reset board
			self.board[x][y] = before
			return False