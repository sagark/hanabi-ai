import random

from card import Card
from constants import HANABI_COLORS, HANABI_SUIT

__author__ = 'julenka'


class Deck:
    """ A deck of cards """

    def __init__(self):
        self.cards = []
        for color in HANABI_COLORS:
            for number in HANABI_SUIT:
                self.cards.append(Card(color, number))
        random.shuffle(self.cards)

    def _draw_card(self):
        """ Returns a card from the top of the deck

        Returns
        card
        """
        return self.draw_cards(1)[0]

    def draw_cards(self, n):
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

    def size(self):
        return len(self.cards)

    def isEmpty(self):
        return len(self.cards) == 0

    def __str__(self):
        return "{} cards\n{}".format(
            len(self.cards),
            ",".join([str(c) for c in self.cards]))