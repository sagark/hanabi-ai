from constants import HANABI_COLORS, HANABI_SUIT

__author__ = 'julenka'


class Guess:
    """ Represents a players guess about a particular card

        fields:
        possible_colors
        possible_numbers
    """
    def __init__(self, possible_colors=None, possible_numbers=None):
        self.possible_colors = possible_colors if possible_colors else HANABI_COLORS
        # WARNING: CODE DUPLICATION
        self.possible_numbers = possible_numbers if possible_numbers else list(set(HANABI_SUIT))

    def set_is_color(self, color):
        if color in self.possible_colors:
            self.possible_colors = [color]

    def set_is_not_color(self, color):
        self.possible_colors = [c for c in self.possible_colors if c != color]

    def set_is_number(self, number):
        if number in self.possible_numbers:
            self.possible_numbers = [number]

    def set_is_not_number(self, number):
        self.possible_numbers = [n for n in self.possible_numbers if n != number]

    def clone(self):
        result = Guess()
        result.possible_numbers = list(self.possible_numbers)
        result.possible_colors = list(self.possible_colors)
        return result

    def __repr__(self):
        return "Guess({},{})".format(self.possible_colors, self.possible_numbers)

    def __str__(self):
        return "{}\t{}".format(",".join([c[0].upper() for c in self.possible_colors]),
                               ",".join([str(x) for x in self.possible_numbers]))