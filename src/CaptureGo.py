import time
import random
import sys
import copy


import numpy as np


from GoBoard import *
from helper import *
from MCTS import *


sys.setrecursionlimit(1000000)


# Helper Function
# Random MC rollouts starting with a board position and node position
def explore_helper(board, node, N):
	board = GoBoard(board)
	while True:
		# Select a valid move and play it
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


def df_explore_helper(board, node):
	board = GoBoard(board)
	if not node.moves:
		node.moves = copy.deepcopy(board.moves)

	while node.moves:
		random.shuffle(node.moves)
		move = node.moves.pop()
		if board.play_move(*move):
			if move in node.children:
				node = node.children[move]
			else:
				new_node = MCTS_Node(node, move)
				node.children[move] = new_node
				node = new_node

			if not node.moves:
				node.moves = copy.deepcopy(board.moves)

	winner = board.winning()
	if winner == BLACK: # Done because WHITE usually have an edge?
		propagate(node, 1)
	elif winner == WHITE:
		propagate(node, 0)
	else:
		propagate(node, 0.5)


class CaptureGo:
	def __init__(self, size=9, komi=5.5):
		self.SIZE = size
		self.N = ((size * size) // 2) + 1
		self.board = GoBoard(size = size, komi = komi)
		self.mcst_root = MCTS_Node(moves=self.board.moves)
		self.step = 0


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
			df_explore_helper(board, node)

	# Return the best move according to the MCST
	# Using prunning
	def pick_best(self):
		if self.board.current_player == BLACK:
			win = 0
		else:
			win = 1

		best = None
		freq = 0
		value = None
		best_min = None
		best_max = None
		for child in self.mcst_root.children:
			node = self.mcst_root.children[child]
			if self.board.current_player == BLACK:
				best, freq, value, best_min, best_max = find_best_black(node, best, freq, value, best_min, best_max)
			else:
				best, freq, value, best_min, best_max = find_best_white(node, best, freq, value, best_min, best_max)

		return best, win ,freq

	def df_explore(self, board, node, budget = 0):
		for i in range(budget):
			df_explore_helper(board, node)

	def recommend(self):
		start = time.time()

		self.df_explore(self.board, self.mcst_root, budget = self.SIZE ** 5)

		end = time.time()

		print("<<< Exploration time: ", end - start, "seconds")

		# Pick the best move based on the exploration
		best, win_rate, freq = self.pick_best()
		if best is None:
			print(self.board.moves)
			return(self.board.moves)

		print("<<< Options explored:", len(self.mcst_root.children))
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
			print("<<< Help on the way!")

		elif command == "d" or command == "display":
			self.display()

		elif command == "q" or command == "quit":
			print("<<< Moriturus te saluto.")
			self.board.w_captures = N + 1

		elif command == "r" or command == "recommend":
			print("<<< Recommended Move: ", self.recommend())

		elif "v" in command:
			command = parse_command_coordinate(command)
			if command and "v" in command[0]:
				x = command[1]
				y = command[2]
				if (x, y) in self.mcst_root.children:
					v = self.mcst_root.children[(x, y)].value
					n = self.mcst_root.children[(x, y)].visited
					print("<<<", v / n, end=' ')
					print(n, "trials")
					print("<<<", self.mcst_root.visited)
				else:
					move = (x, y)
					print("<<<", move, "is unexplored.")

		elif "p" in command:
			command = parse_command_coordinate(command)
			if command and "p" in command[0]:
				x = command[1]
				y = command[2]
				played = self.board.play_move(x, y)

				if played == False:
					print("<<< Bad move, try again")
				else:
					self.step += 1

					if (x, y) not in self.mcst_root.children:
						self.mcst_root.children[(x, y)] = MCTS_Node(self.mcst_root, (x, y))

					self.mcst_root = self.mcst_root.children[(x, y)]
					self.mcst_root.parent = None
					print("<<<", self.mcst_root.get_win_rate())
					print("<<<", self.mcst_root.visited, "trials")

		else:
			print("<<< Bad command")
