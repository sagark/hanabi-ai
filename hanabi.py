#!/usr/bin/env python

""" Simulates a game of hanabi, allowing for experimentation of different hanabi strategies assuming perfect memory """

import random

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

class Card:
	""" A card in Hanabi """
	def __init__(self, color, number):
		""" A Hanabi card has a color and number """
		self.color = color
		self.number = number

	def __repr__(self):
		return "Card({},{})".format(self.color, self.number)

class Guess:
	""" Represents a players guess about a particular card """
	def __init__(self):
		self.possible_colors = HANABI_COLORS
		# WARNING: CODE DUMPLICATION
		self.possible_numbers = set(HANABI_SUIT)

	def __str__(self):
		return "{}\t{}".format(self.possible_colors, self.possible_numbers)

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
	def __init__(self, cards):
		# cards in hand
		self.cards = cards
		# guesses about cards
		self.guesses = [Guess() for c in self.cards]

	def __str__(self):
		lines = ["card: {}\tguess: {}".format(card, guess) for card, guess in zip(self.cards, self.guesses) ]
		return "\n".join(lines)

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
		for _ in xrange(n_players):
			self.players.append(Player(self.deck.drawCards(CARDS_PER_PLAYER[n_players])))

	def printHeader(self, header):
		separator = "*" * 40
		print
		print separator
		print header
		print separator

	def show(self):
		self.printHeader("Players")
		for i,p in enumerate(self.players):
			print "Player {}".format(i)
			print str(p)

		self.printHeader("Deck")
		print str(self.deck)

game = Game(4)
game.show()
