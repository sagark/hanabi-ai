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

EVALUATION_TIMES = 10000
def evaluateStrategy(strategy, n_players):
	import matplotlib.pyplot as plt
	import seaborn as sns
	import numpy as np
	scores = []
	for i in xrange(EVALUATION_TIMES):
		game = Game(n_players)
		game.strategy = strategy
		score = game.playEntireGame()
		scores.append(score)
	print scores
	bins = np.linspace(0,25,26)
	plt.hist(scores, bins)
	plt.show()
	


# testStrategy(InteractiveStrategy())
# testStrategy(PlayZerothStrategy())
# testStrategy(Strategy1())
# evaluateStrategy(PlayZerothStrategy(), 3)
testStrategy(Strategy1())
