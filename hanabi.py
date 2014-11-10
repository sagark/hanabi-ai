#!/usr/bin/env python

""" Simulates a game of hanabi, allowing for experimentation of different hanabi strategies assuming perfect memory """

from collections import defaultdict
import random
import re
import logging 

logging.basicConfig()
logger = logging.getLogger('hanabi')
logger.setLevel(logging.DEBUG)

# TODO: MAKE COLORS AND MOVES ENUMS OR CONSTANTS

# Globals specific to game
HANABI_COLORS = ["red", "blue", "green", "yellow", "white"]
HANABI_SUIT = [1,1,1,2,2,3,3,4,4,5]
N_CARDS_PER_SUIT = len(set(HANABI_SUIT))
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

	def __eq__(self, other):
		return self.number == other.number and self.color == other.color

	def __repr__(self):
		return "Card({},{})".format(self.color, self.number)

class Guess:
	""" Represents a players guess about a particular card 

		fields:
		possible_colors
		possible_numbers
	"""
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
			raise Exception("drawCards({}) called when only {} cards in deck".format(n, len(self.cards) ))
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
	def __init__(self, cards, name, index):
		# cards in hand
		self.cards = cards
		# guesses about cards
		self.guesses = [Guess() for c in self.cards]
		self.name = name
		self.index = index

	def play(self, i, t):
		''' Play a card at index i on table t'''
		t.playCard(self.cards[i])
		self.removeCard(i)

	def removeCard(self, i):
		del self.cards[i]
		del self.guesses[i]

	def discard(self, i, t):
		t.discard(self.cards[i])
		self.removeCard(i)


	def getPlayableCards(self, table):
		''' Return the indices of all playable card in this hand '''
		return [i for i,card in enumerate(self.cards) if table.canPlayCard(card)]

	def drawCard(self, deck):
		if not deck.isEmpty() > 0:
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
	def __init__(self, cards_on_table=None,num_fuse_tokens=INITIAL_NUM_FUSE_TOKENS,
		num_clock_tokens=INITIAL_NUM_CLOCK_TOKENS,discard_pile=None):
		# data is a map from color -> cards
		self.cards_on_table = {c: [] for c in HANABI_COLORS}
		self.num_fuse_tokens = num_fuse_tokens
		self.num_clock_tokens = num_clock_tokens
		self.discard_pile = [] if not discard_pile else discard_pile

	def playCard(self, card):
		""" Plays a card on the table, assuming it is valid.

		If not valid, throw exception
		"""
		if not self.canPlayCard(card):
			self.num_fuse_tokens -= 1
			logger.debug("***BOOM*** Booms left: {}".format(self.num_fuse_tokens))
			self.discard(card)
		else:
			self.cards_on_table[card.color].append(card)

	def canPlayCard(self, card):
		playable_cards = self.getPlayableCards()
		return card in playable_cards

	def getPlayableCards(self):
		playable_cards = []
		for color, cards in self.cards_on_table.iteritems():
			if len(cards) >= N_CARDS_PER_SUIT:
				continue
			next_number = len(cards) + 1
			playable_cards.append(Card(color, next_number))
		return playable_cards

	def discard(self, card):
		self.discard_pile.append(card)

	def getScore(self):
		print "getScore: ", self.cards_on_table
		numbers_for_colors = ([c.number for c in cards] for cards in self.cards_on_table.values())
		return sum((max(x) if len(x) > 0 else 0 for x in numbers_for_colors))

	def __repr__(self):
		return "Table(cards_on_table={},num_fuse_tokens={},num_clock_tokens={},discard_pile={})".format(self.cards_on_table,self.num_fuse_tokens,
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
			self.players.append(Player(self.deck.drawCards(CARDS_PER_PLAYER[n_players]), "player {}".format(i), i ))

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
			other_players, self.table, logger)
		cur_player_object = self.players[self.cur_player]
			
		if method == "discard":
			idx = int(params)
			logger.debug("{} discarding {}".format(cur_player_object.name, cur_player_object.cards[idx]))
			cur_player_object.discard(idx, self.table)
			cur_player_object.drawCard(self.deck)
		elif method == "play":
			idx = int(params)
			logger.debug("{} playing {}".format(cur_player_object.name, cur_player_object.cards[idx]))
			cur_player_object.play(idx, self.table)
			cur_player_object.drawCard(self.deck)
		elif method.startswith("say"):
			idx,arg = params
			if self.table.num_clock_tokens == 0:
				raise Exception("player {} called 'say' with no information tokens left".format(cur_player.index))
			if idx == self.cur_player:
				raise Exception("player {} is trying to tell itself information".format(idx))
			# TODO: you can never give information about 0 cards. Throw exception
			logger.debug("{} saying {},{}".format(cur_player_object.name, idx, arg))
			self.say(idx, arg)
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
		if len(self.table.getPlayableCards()) == 0:
			self.gameOverReason = "****YOU GOT A PERFECT SCORE****"
		return self.gameOverReason

	def doGameOver(self):
		self.printHeader("Game Over")
		print "reason: {}".format(self.gameOverReason)

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
		return self.table.getScore()

