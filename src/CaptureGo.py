# TODO: Add prunning methods -- don't choose a move with a good opponent followup


import numpy as np


import random
import time # Delete this later
import sys

from GoBoard import *
from MCTS import MCTS_Node


sys.setrecursionlimit(1000000)


# Required Captures
SIZE = 9
N = (SIZE * SIZE) // 2 + 1 # ~ SIZE * SIZE / 2


# Helper Function
# Propagate value up the MCST
def propagate(node, value):
	if node.value == None:
		node.value = value
	else:
		node.value += value

	node.visited += 1

	if node.parent:
		propagate(node.parent, value)

# Helper Function
# Random MC rollouts starting with a board position and node position
def explore_helper(board, node):
	board = GoBoard(board)
	while True:
		# Select a valid move and play it
		# Randomize the move order
		# Equivalent result to random.choice, but this way we can see if there
		# are no valid moves.
		random.shuffle(board.moves)
		random.shuffle(board.moves)
		random.shuffle(board.moves)
		play = False
		move = None
		for i in range(len(board.moves)):
			move = board.moves[i]
			play = board.play_move(*move)
			if play:
				break

		# No more legal move -> end of the game
		if play == False:
			if board.w_captures > board.b_captures: # Alternative judgement
			# if board.current_player == BLACK: # Since can't make a move
				propagate(node, 0)
			else:
				propagate(node, 1)

			break

		# Move down the game tree
		if move in node.children:
			node = node.children[move]
		else:
			new_node = MCTS_Node(node, move)
			node.children[move] = new_node
			node = new_node

		# Check if reached the end of the game, and deal with it
		# Otherwise, loop until we reach the end
		if board.w_captures > N: # "white pseudo-victory"
			propagate(node, 0)
			break
		elif board.b_captures > N: # "black pseudo-victory"
			propagate(node, 1)
			break


class CaptureGo:
	def __init__(self):
		self.board = GoBoard()
		self.mcst_root = MCTS_Node()
		self.step = 0

	# move must be a valid move on the current board
	def explore(self, budget, move = None):
		# Fix the right starting point
		board = GoBoard(self.board)
		node = self.mcst_root

		if move:
			play = board.play_move(*move)
			if not play:
				return
			if move in node.children:
				node = node.children[move]
			else:
				node.children[move] = MCTS_Node(node, move)
				node = node.children[move]

		# Explore budget number of times and let explore_helper build the tree
		for i in range(budget):
			explore_helper(board, node)

	# Return the best move according to the MCST
	def pick_best(self):
		if self.board.current_player == BLACK:
			win = 0
		else:
			win = 1

		best = None
		freq = 0
		for child in self.mcst_root.children:
			n, v, move = self.mcst_root.children[child].get_evaluation()
			new_win = v / n
			if self.board.current_player == BLACK:
				if new_win > win:
					win = new_win
					freq = n
					best = move
				elif new_win == win:
					if n > freq:
						win = new_win
						freq = n
						best = move
			else:
				if new_win < win:
					win = new_win
					freq = n
					best = move
				elif new_win == win:
					if n > freq:
						win = new_win
						freq = n
						best = move

		return best, win ,freq

	def recommend(self):
		# Explore
		# self.explore(len(self.board.moves) ** 2)

		start = time.time()
		self.explore(1000)

		# Explore every possible move; too slow
		# for move in self.board.moves:
		# 	if move in self.mcst_root.children:
		# 		n = self.mcst_root.children[move].visited
		# 	else:
		# 		n = 0
		#
		# 	self.explore((SIZE * SIZE * 2) - n, move)
		end = time.time()

		print("Exploration time: ", end - start, "seconds")

		# Pick the best move based on the exploration
		best, win_rate, freq = self.pick_best()

		if freq < SIZE * SIZE * 2 and best is not None:
			print("Considering")
			start = time.time()
			self.explore((SIZE * SIZE * 2) - freq, best)
			end = time.time()
			print("Consideration time: ", end - start, "seconds")

			n, v, move = self.mcst_root.children[best].get_evaluation()
			if self.board.current_player == BLACK and (v / n) < 0.5:
				print("Re-exploring")
				return self.recommend()
			elif self.board.current_player == WHITE and (v / n) > 0.5:
				print("Re-exploring")
				return self.recommend()

		# print("Options explored: ", len(self.mcst_root.children))
		return best

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

		print(self.step, "moves played.")
		if self.board.current_player == BLACK:
			print("Black to play.")
		else:
			print("White to play.p")
		print(self.mcst_root.identity, "was played.")

	def handle_command(self, command):
		if command == "h" or command == "help":
			print("Helpful message")

		elif command == "q" or command == "quit":
			self.board.w_captures = N + 1

		elif command == "r" or command == "recommend":
			print("Recommended Move: ", self.recommend())

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
					self.step += 1

					if (x, y) not in self.mcst_root.children:
						self.mcst_root.children[(x, y)] = MCTS_Node(self.mcst_root, (x, y))

					self.mcst_root = self.mcst_root.children[(x, y)]
					self.mcst_root.parent = None
					print(self.mcst_root.get_win_rate())
					print(self.mcst_root.visited)

			else:
				print("Bad move")
