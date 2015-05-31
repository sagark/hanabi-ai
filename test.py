#!/usr/bin/env python
""" Implements some very basic tests I ran during development.


Note these are not unit tests as there is currently no way to control specifics of game state.

"""
from game import Game

import unittest


class TestGame(unittest.TestCase):
    def test_show_game(self):
        game = Game(3)
        game.show()


if __name__ == '__main__':
    unittest.main()