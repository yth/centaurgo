import collections


class MCTS_Node:
	def __init__(self, parent = None, identity = None, moves = None):
		self.parent = parent
		self.identity = identity
		self.visited = 0
		self.value = None
		self.children = {}
		self.moves = None

	def get_evaluation(self):
		return (self.visited, self.value, self.identity)

	# TODO: Why does this segfault
	def get_size(self, node):
		size = 1
		for child in self.children:
			size += self.get_size(self.children[child])
		return size

	def get_win_rate(self):
		if self.visited:
			return self.value / self.visited
		else:
			return "Unknown win rate"

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

