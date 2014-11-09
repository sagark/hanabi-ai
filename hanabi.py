#!/usr/bin/env python

""" Simulates a game of hanabi, allowing for experimentation of different hanabi strategies assuming perfect memory """

from collections import defaultdict
import random
import re
import logging 

logging.basicConfig()
logger = logging.getLogger('hanabi')
logger.setLevel(logging.DEBUG)

# Components
# Deck
# Card
# Player
# Game
# Strategy

# Globals specific to game
HANABI_COLORS = ["red", "blue", "green", "yellow", "white"]
HANABI_SUIT = [1,1,1,2,2,3,3,4,4,5]
# If there are 2 or 3 players, each player receives 5 cards. If there are 4 or 5 players, each player receives 4 cards.
CARDS_PER_PLAYER = {2:5,3:5,4:4,5:4}

INITIAL_NUM_CLOCK_TOKENS = 8
INITIAL_NUM_FUSE_TOKENS = 3
# INITIAL_NUM_FUSE_TOKENS = 0

class Card:
	""" A card in Hanabi 
	
	A Hanabi card has a color and number
	"""
	def __init__(self, color, number):
		self.color = color
		self.number = number

	def __repr__(self):
		return "Card({},{})".format(self.color, self.number)

class Guess:
	""" Represents a players guess about a particular card """
	def __init__(self, possible_colors=None, possible_numbers=None):
		self.possible_colors = possible_colors if possible_colors else HANABI_COLORS
		# WARNING: CODE DUMPLICATION
		self.possible_numbers = possible_numers if possible_numbers else list(set(HANABI_SUIT))

	def setIsColor(self, color):
		self.possible_colors = [color]

	def setIsNotColor(self, color):
		self.possible_colors = [c for c in self.possible_colors if c != color]

	def setIsNumber(self, number):
		self.possible_numbers = [number]

	def setIsNotNumber(self, number):
		self.possible_numbers = [n for n in self.possible_numbers if n != number]
	
	def __repr__(self):
		return "Guess({},{})".format(self.possible_colors, self.possible_numbers)

class Deck:
	""" A deck of cards """
	
	def __init__(self):
		self.cards = []
		for color in HANABI_COLORS:
			for number in HANABI_SUIT:
				self.cards.append(Card(color, number))
		random.shuffle(self.cards)

	def drawCard(self):
		""" Returns a card from the top of the deck 

		Returns
		card
		"""
		return self.drawCards(1)[0]

	def drawCards(self,n):
		""" Draw n cards from the top of the deck 

		Returns:
		[card1, card2, ... , cardn]
		"""
		if n > len(self.cards):
			raise Exception("drawCards({}) called when only {} cards in deck".format(n, len(cards)))
		if n < 0:
			raise Exception("drawCards({}) can't use negative number".format(n))
		result = self.cards[-n:]
		del self.cards[-n:]
		return result

	def isEmpty(self):
		return len(self.cards) == 0

	def __str__(self):
		return "{}".format(self.cards)

class Player:
	""" A player in Hanabi """
	def __init__(self, cards, name):
		# cards in hand
		self.cards = cards
		# guesses about cards
		self.guesses = [Guess() for c in self.cards]
		self.name = name

	def play(self, i, t):
		''' Play a card at index i on table t'''
		logger.debug("{} playing {}".format(self.name, self.cards[i]))
		t.playCard(self.cards[i])
		self.removeCard(i)

	def removeCard(self, i):
		del self.cards[i]
		del self.guesses[i]

	def discard(self, i, t):
		logger.debug("{} discarding {}".format(self.name, self.cards[i]))
		t.discard(self.cards[i])
		self.removeCard(i)


	def getPlayableCards(self, table):
		''' Return the indices of all playable card in this hand '''
		return [i for i,card in enumerate(self.cards) if table.canPlayCard(card)]

	def drawCard(self, deck):
		self.cards.append(deck.drawCard())
		self.guesses.append(Guess())

	def receiveColorInfo(self, color):
		''' Another player has told this player about all cards of a particular color.

		Update all guesses to reflect this information'''
		for guess, actual in zip(self.guesses,self.cards):
			if actual.color == color:
				guess.setIsColor(color)
			else:
				guess.setIsNotColor(color)

	def receiveNumberInfo(self, number):
		''' Another player has told this player about all cards of a particular number.

		Update all guesses to reflect this information'''
		for guess, actual in zip(self.guesses,self.cards):
			if actual.number == number:
				guess.setIsNumber(number)
			else:
				guess.setIsNotNumber(number)

	def __str__(self):
		# on each line, print the actual card and guess for that card
		lines = ["{}\t{}".format(card, guess) for card, guess in zip(self.cards, self.guesses) ]
		print self.name
		return "\n".join(lines)

class Table:
	""" Represents the game table, e.g. the area where cards are played """
	def __init__(self, data=defaultdict(list),num_fuse_tokens=INITIAL_NUM_FUSE_TOKENS,
		num_clock_tokens=INITIAL_NUM_CLOCK_TOKENS,discard_pile=[]):
		# data is a map from color -> cards
		self.data = data;
		self.num_fuse_tokens = num_fuse_tokens
		self.num_clock_tokens = num_clock_tokens
		self.discard_pile = discard_pile

	def playCard(self, card):
		""" Plays a card on the table, assuming it is valid.

		If not valid, throw exception
		"""
		if not self.canPlayCard(card):
			self.num_fuse_tokens -= 1
			logger.debug("***BOOM*** Booms left: {}".format(self.num_fuse_tokens))
			self.discard(card)
		else:
			self.data[card.color].append(card)

	def canPlayCard(self, card):
		color = card.color
		number = card.number
		num_cards_in_color = len(self.data[color])
		return (num_cards_in_color + 1) == number

	def discard(self, card):
		self.discard_pile.append(card)

	def getScore(self):
		print "getScore: ", self.data.values()
		numbers_for_colors = ((c.number for c in cards) for cards in self.data.values())
		return sum((sum(x) for x in numbers_for_colors))

	def __repr__(self):
		return "Table(data={},num_fuse_tokens={},num_clock_tokens={},discard_pile={})".format(self.data,self.num_fuse_tokens,
			self.num_clock_tokens, self.discard_pile)

class Game:
	def __init__(self, n_players):
		""" Build game of Hanabi

		Args:
		n_players -- How many n_players
		"""
		if n_players not in CARDS_PER_PLAYER:
			raise Exception ("Num players must be between 2 and 5")
		self.deck = Deck()
		self.players = []

		# Game is over is num fuse or num clock tokens goes below zero
		self.cur_player = 0
		
		self.table = Table()
		self.num_turns_left = None 
		for i in xrange(n_players):
			self.players.append(Player(self.deck.drawCards(CARDS_PER_PLAYER[n_players]), "player {}".format(i)))

	def say(self, idx, param):
		try:
			number = int(param)
			self.players[idx].receiveNumberInfo(number)
		except ValueError:
			self.players[idx].receiveColorInfo(param)
			
		self.table.num_clock_tokens -= 1


	def doTurn(self):
		if self.strategy is None:
			raise Exception("doTurn called but no player strategy specified")
		# do the turn
		other_players = [p for i,p in enumerate(self.players) if i != self.cur_player]
		method, params = self.strategy.doTurn(self.cur_player, self.players[self.cur_player].guesses,
			other_players, self.table)

		if method.startswith("say"):
			idx,color = params
			self.say(idx, color)
		elif method == "discard":
			idx = int(params)
			self.players[self.cur_player].discard(idx, self.table)
			self.players[self.cur_player].drawCard(self.deck)
		elif method == "play":
			idx = int(params)
			self.players[self.cur_player].play(idx, self.table)
			self.players[self.cur_player].drawCard(self.deck)
		else:
			raise Exception("Invalid command retured from strategy.doTurn: {}", command)


		# current player draw card
		# check if deck is empty, if so, don't draw, instead start countdown
		if self.deck.isEmpty():
			if self.num_turns_left is None:
				self.num_turns_left = len(self.players)
			else:
				self.num_turns_left -= 1

		self.cur_player += 1
		self.cur_player %= len(self.players)

	def isGameOver(self):
		''' Check whether game is over

		Ways game can be over:
		deck is empty and n_players moves have been executed


		Returns:
		None if game is not over
		String explaining game over reason is over'''
		self.gameOverReason = None
		if self.num_turns_left is not None and self.num_turns_left == 0:
			self.gameOverReason = "Deck is empty and out of turns"
		if self.table.num_clock_tokens < 0:
			self.gameOverReason = "Tried to use information when no information was left"
		if self.table.num_fuse_tokens < 0:
			self.gameOverReason = "Explosion when no fuse tokens left"
		return self.gameOverReason

	def doGameOver(self):
		self.printHeader("Game Over")
		print "reason: {}".format(self.gameOverReason)
		print "score: {}".format(self.table.getScore())

	def printHeader(self, header):
		separator = "*" * 40
		print
		print separator
		print header
		print separator

	def show(self):
		self.printHeader("BEGIN GAME STATE")
		self.printHeader("Players")
		for p in self.players:
			print str(p)

		self.printHeader("Deck")
		print self.deck

		self.printHeader("Table")
		print self.table

		print
		print "cur_player: {}".format(self.cur_player)
		
		self.printHeader("END GAME STATE")
		print

	def playEntireGame(self):
		''' Plays the entire game assuming a strategy is set

		1. Check if strategy is set
		2. Loop and play game until game is over
		'''
		if not self.strategy:
			raise Exception ("playEntireGame called but no strategy was set!")

		while (not self.isGameOver()):
			self.doTurn()
		self.doGameOver()

