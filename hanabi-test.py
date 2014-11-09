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


def testStrategy(strategy):
	# game loop:
	game = Game(3)
	game.strategy = strategy
	score = game.playEntireGame()
	print "final score: ", score

def evaluateStrategy(strategy, n_players):
	import matplotlib.pyplot as plt
	import seaborn as sns
	scores = []
	for i in xrange(1000):
		game = Game(n_players)
		game.strategy = strategy
		score = game.playEntireGame()
		scores.append(score)
	print scores
	plt.hist(scores)
	plt.show()
	


# testStrategy(InteractiveStrategy())
# testStrategy(PlayZerothStrategy())
# testStrategy(Strategy1())
evaluateStrategy(PlayZerothStrategy(), 3)
