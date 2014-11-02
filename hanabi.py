#!/usr/bin/env python

""" Simulates a game of hanabi, allowing for experimentation of different hanabi strategies assuming perfect memory """

from collections import defaultdict
import random
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
INITIAL_NUM_FUSE_TOKENS = 4

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
		return self.drawCard(1)[0]

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
		del self.cards[i]

	def getPlayableCards(self, table):
		''' Return the indices of all playable card in this hand '''
		return [i for i,card in enumerate(self.cards) if table.canPlayCard(card)]

	def drawCard(self, deck):
		self.cards.append(deck.drawCard())

	def __str__(self):
		# on each line, print the actual card and guess for that card
		lines = ["{}\t{}".format(card, guess) for card, guess in zip(self.cards, self.guesses) ]
		print self.name
		return "\n".join(lines)

class Table:
	""" Represents the game table, e.g. the area where cards are played """
	def __init__(self, data=None):
		# data is a map from color -> cards
		if data:
			self.data = data
		else:
			self.data = defaultdict(list)

	def playCard(self, card):
		""" Plays a card on the table, assuming it is valid.

		If not valid, throw exception
		"""
		if not self.canPlayCard(card):
			raise Exception("playCard invalid card: {}, current table is {}".format(card, self))
		self.data[card.color].append(card)

	def canPlayCard(self, card):
		color = card.color
		number = card.number
		num_cards_in_color = len(self.data[color])
		return num_cards_in_color + 1 == number

	def __repr__(self):
		return "Table(data={})".format(self.data)

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
		self.num_fuse_tokens = INITIAL_NUM_FUSE_TOKENS
		self.num_clock_tokens = INITIAL_NUM_CLOCK_TOKENS

		self.cur_player = 0
		self.discard_pile = []
		self.table = Table()

		for i in xrange(n_players):
			self.players.append(Player(self.deck.drawCards(CARDS_PER_PLAYER[n_players]), "player {}".format(i)))

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
		print "discard pile: {}".format(self.discard_pile)
		print "num_fuse_tokens: {}".format(self.num_fuse_tokens)
		print "num_clock_tokens: {}".format(self.num_clock_tokens)
		self.printHeader("END GAME STATE")
		print

