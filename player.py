from guess import Guess

__author__ = 'julenka'


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
        print "card\tpossible_colors\tpossible_numbers"
        return "\n".join(lines)