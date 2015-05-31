__author__ = 'julenka'


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

    def __str__(self):
        return "{}{}".format(self.color[0].upper(), self.number)