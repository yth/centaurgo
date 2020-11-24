import unittest
import sys


sys.path.insert(0, "../")


from centaurgo.src.GoBoard import *


class GoBoardTests(unittest.TestCase):
	def setUp(self):
		self.board = GoBoard()

	def tearDown(self):
		del self.board

	def test_empty_constructor(self):
		self.assertFalse(self.board == None)
		self.assertTrue(len(self.board.board) == 9)
		self.assertTrue(len(self.board.board[0]) == 9)
		self.assertTrue(self.board.w_captures == 5.5)
		self.assertTrue(self.board.b_captures == 0)

	def test_place_marker(self):
		self.board.place_marker(BLACK, 0, 0)
		self.assertTrue(self.board.board[0][0] == BLACK)

		self.board.place_marker(WHITE, 0, 0)
		self.assertTrue(self.board.board[0][0] == WHITE)

		self.board.place_marker(9, 0, 0)
		self.assertTrue(self.board.board[0][0] == 9)

	def test_copy_constructor(self):
		# Make a copy
		self.board.place_marker(BLACK, 0, 0)
		new_board = GoBoard(self.board)
		self.assertTrue(new_board.board[0][0] == BLACK)

		# New board is not related to the old board
		new_board.place_marker(BLACK, 1, 1)
		self.assertFalse(self.board.board[1][1] == BLACK)

	def test_list_liberties(self):
		self.board.place_marker(BLACK, 0, 0)
		self.assertTrue(len(self.board.list_liberties(0, 0)) == 2)

		self.board.place_marker(WHITE, 5, 5)
		self.assertTrue(len(self.board.list_liberties(5, 5)) == 4)

		self.board.place_marker(BLACK, 5, 4)
		self.assertTrue(len(self.board.list_liberties(5, 5)) == 3)

		self.board.place_marker(WHITE, 5, 6)
		self.assertTrue(len(self.board.list_liberties(5, 5)) == 5)

		self.board.place_marker(WHITE, 6, 4)
		self.assertTrue(len(self.board.list_liberties(5, 5)) == 5)
		self.assertTrue(len(self.board.list_liberties(6, 4)) == 3)

	def test_play_move_basic(self):
		self.board.play_move(0, 0)
		self.board.play_move(1, 0)
		self.assertFalse(self.board.play_move(9, 9))
		self.assertFalse(self.board.play_move(-1, 7))
		self.assertFalse(self.board.play_move(0, 0))
		self.board.play_move(8, 8)
		self.board.play_move(0, 1)
		self.assertTrue(self.board.board[0][0] == BLACK_KO)
		self.assertTrue(self.board.w_captures == 6.5)

	def test_play_move_capture_2_return_1(self):
		self.assertTrue(self.board.play_move(4, 2))
		self.assertTrue(self.board.play_move(4, 6))
		self.assertTrue(self.board.play_move(3, 3))
		self.assertTrue(self.board.play_move(4, 3))
		self.assertTrue(self.board.play_move(5, 3))
		self.assertTrue(self.board.play_move(3, 5))
		self.assertTrue(self.board.play_move(3, 4))
		self.assertTrue(self.board.play_move(4, 4))
		self.assertTrue(self.board.play_move(5, 4))
		self.assertTrue(self.board.play_move(5, 5))
		self.assertTrue(self.board.play_move(4, 5))
		self.assertTrue(self.board.play_move(4, 4))

		self.assertTrue(self.board.w_captures == 6.5)
		self.assertTrue(self.board.b_captures == 2)

		self.assertTrue(self.board.play_move(4, 3))
		self.assertTrue(self.board.board[4][5] == 0)


if __name__ == "__main__":
	unittest.main()