class MCTS_Node:
	def __init__(self, parent = None, identity = None):
		self.parent = parent
		self.identity = identity
		self.visited = 0
		self.value = None
		self.children = {}

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