#!/usr/bin/env python
''' Implements some very basic tests I ran during development. 


Note these are not unit tests as there is currently no way to control specifics of game state.

'''

from hanabi import *
from strategies import *

def testPlayCard():
	''' Tests whether players can play cards on the table '''
	print "testPlayCard start"
	game = Game(3)
	# test playing to a deck
	cur = game.players[game.cur_player]
	playable_cards = cur.getPlayableCards(game.table)
	while len(playable_cards) > 0:
		cur.play(playable_cards[0], game.table)
		game.show()
		game.cur_player += 1
		game.cur_player %= len(game.players)
		cur = game.players[game.cur_player]
		playable_cards = cur.getPlayableCards(game.table)
	print "testPlayCard end"
	
def testShowGame():
	game = Game(3)
	game.show()


def testInteractiveStrategy():
	# game loop:
	game = Game(3)
	game.strategy = InteractiveStrategy()
	gameOver = game.isGameOver()
	while (not gameOver):
		game.doTurn()
		# game.show()
		gameOver = game.isGameOver()
	game.doGameOver(gameOver)

testInteractiveStrategy()
