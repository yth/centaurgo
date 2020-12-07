# TODO: Add prunning methods -- don't choose a move with a good opponent followup


import numpy as np


import random
import time # Delete this later
import sys

from GoBoard import *
from MCTS import MCTS_Node


sys.setrecursionlimit(1000000)


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
def explore_helper(board, node, N):
	board = GoBoard(board)
	while True:
		# Select a valid move and play it
		# Randomize the move order
		# Equivalent result to random.choice, but this way we can see if there
		# are no valid moves.
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

# Find the next move with the smallest win rate for black
def find_min_value_child(node):
	min_move = None
	freq = 0
	win = 1
	for child in node.children:
		n, v, move = node.get_evaluation()
		new_win = v / n

		if new_win < win:
			win = new_win
			freq = n
			min_move = move
		elif new_win == win and n > freq: # Use the more certain move
			freq = n
			min_move = move

	return min_move, freq, win

# Find the next move with the smallest win rate for black
def find_max_value_child(node):
	max_move = None
	freq = 0
	win = 0
	for child in node.children:
		n, v, move = node.get_evaluation()
		new_win = v / n

		if new_win > win:
			win = new_win
			freq = n
			max_move = move
		elif new_win == win and n > freq: # Use the more certain move
			freq = n
			max_move = move

	return max_move, freq, win


class CaptureGo:
	def __init__(self, size=9, komi=5.5):
		self.SIZE = size
		self.N = ((size * size) // 2) + 1
		self.board = GoBoard(size = size, komi = komi)
		self.mcst_root = MCTS_Node()
		self.step = 0
		print("GOT HERE2")
		print(self.N)
		print(self.N)

	# move must be a valid move on the current board
	def explore(self, budget, move1 = None, move2 = None):
		# Fix the right starting point
		board = GoBoard(self.board)
		node = self.mcst_root

		if move1:
			play = board.play_move(*move1)
			if not play:
				return
			elif move1 in node.children:
				node = node.children[move1]
			else:
				node.children[move1] = MCTS_Node(node, move1)
				node = node.children[move1]

		if move2:
			play = board.play_move(*move2)
			if not play:
				return
			elif move2 in node.children:
				node = node.children[move2]
			else:
				node.children[move2] = MCTS_Node(node, move2)
				node = node.children[move2]

		# Explore budget number of times and let explore_helper build the tree
		for i in range(budget):
			explore_helper(board, node, self.N)

	# Return the best move according to the MCST
	# Using prunning
	def pick_best(self):
		if self.board.current_player == BLACK:
			win = 0
		else:
			win = 1

		best = None
		freq = 0
		for child in self.mcst_root.children:
			node = self.mcst_root.children[child]
			if self.board.current_player == BLACK:
				min_move, min_freq, min_win = find_min_value_child(node)
				if min_win > win:
					win = min_win
					best = min_move
					freq = min_freq
				elif min_win == win and min_freq > freq:
					best = min_move
					freq = min_freq
			else:
				max_move, max_freq, max_win = find_max_value_child(node)
				if max_win < win:
					win = max_win
					best = max_move
					freq = max_freq
				elif max_win == win and max_freq > freq:
					best = max_move
					freq = max_freq

		return best, win ,freq

	def recommend(self):
		# Explore
		# self.explore(len(self.board.moves) ** 2)

		start = time.time()
		# self.explore(10)

		# Explore every possible move first play; too slow
		for move1 in self.board.moves:
			for move2 in self.board.moves:
				n = 0
				if move1 in self.mcst_root.children:
					node = self.mcst_root.children[move1]
					if move2 in node.children:
						n = node.children[move2].visited

				# self.explore((SIZE * SIZE * 2) - n, move)
				self.explore(SIZE - n, move1, move2)

		end = time.time()

		print("Exploration time: ", end - start, "seconds")

		# Pick the best move based on the exploration
		best, win_rate, freq = self.pick_best()
		if best is None:
			print(self.board.moves)
			return(self.board.moves)


		# if freq < SIZE * SIZE * 2:
		# 	print("Considering")
		# 	start = time.time()
		# 	self.explore((SIZE * SIZE * 2) - freq, best)
		# 	end = time.time()
		# 	print("Consideration time: ", end - start, "seconds")
		#
		# 	node = self.mcst_root.children[best]
		# 	if self.board.current_player == BLACK:
		# 		_, _, win = find_min_value_child(node)
		# 		if win < 0.5:
		# 			print("Re-exploring")
		# 			return self.recommend()
		# 	else: # WHITE
		# 		_, _, win = find_max_value_child(node)
		# 		if win > 0.5:
		# 			print("Re-exploring")
		# 			return self.recommend()

		# print("Options explored: ", len(self.mcst_root.children))
		return best

	def has_won(self):
		if self.board.w_captures > self.N or self.board.b_captures > self.N:
			return True
		return False

	def display(self):
		s = "   " + ' '.join(map(str, list(range(self.SIZE))))
		print(s)
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
			print("White to play.")
		print(self.mcst_root.identity, "was played.")

	def handle_command(self, command):
		if command == "h" or command == "help":
			print("Helpful message")

		elif command == "q" or command == "quit":
			self.board.w_captures = N + 1

		elif command == "r" or command == "recommend":
			print("Recommended Move: ", self.recommend())

		elif "v" in command:
			command = command.split()
			if "v" in command[0] and len(command) == 3:
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

			if (x, y) in self.mcst_root.children:
				v = self.mcst_root.children[(x, y)].value
				n = self.mcst_root.children[(x, y)].visited
				print(v / n)
			else:
				move = (x, y)
				print(move, "is unexplored.")

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
