from guess import Guess

__author__ = 'julenka'


class Player:
    """ A player in Hanabi """
    def __init__(self, cards, name, index):
        self.cards = cards
        self.guesses = [Guess() for c in self.cards]
        self.name = name
        self.index = index

    def play(self, i, t):
        """Play a card at index i on table t"""
        t.play_card(self.cards[i])
        self.remove_card(i)

    def remove_card(self, i):
        del self.cards[i]
        del self.guesses[i]

    def discard(self, i, t):
        t.discard(self.cards[i])
        self.remove_card(i)

    def get_playable_cards(self, table):
        """ Return the indices of all playable card in this hand """
        return [i for i, card in enumerate(self.cards) if table.can_play_card(card)]

    def draw_card(self, deck):
        if not deck.is_empty() > 0:
            self.cards.append(deck._draw_card())
            self.guesses.append(Guess())

    def receive_color_info(self, color):
        """ Another player has told this player about all cards of a particular color.

        Update all guesses to reflect this information"""
        for guess, actual in zip(self.guesses,self.cards):
            if actual.color == color:
                guess.set_is_color(color)
            else:
                guess.set_is_not_color(color)

    def receive_number_info(self, number):
        """ Another player has told this player about all cards of a particular number.

        Update all guesses to reflect this information"""
        for guess, actual in zip(self.guesses,self.cards):
            if actual.number == number:
                guess.set_is_number(number)
            else:
                guess.set_is_not_number(number)

    def __str__(self):
        # on each line, print the actual card and guess for that card
        lines = ["{}\t{}".format(card, guess) for card, guess in zip(self.cards, self.guesses) ]
        print self.name
        print "card\tpossible_colors\tpossible_numbers"
        return "\n".join(lines)