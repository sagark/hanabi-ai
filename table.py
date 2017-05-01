from card import Card
from constants import INITIAL_NUM_FUSE_TOKENS, INITIAL_NUM_CLOCK_TOKENS, HANABI_COLORS, N_CARDS_PER_SUIT
from log import logger
__author__ = 'julenka'


class Table:
    """ Represents the game table, e.g. the area where cards are played """
    def __init__(self,
                 cards_on_table=None,
                 num_fuse_tokens=INITIAL_NUM_FUSE_TOKENS,
                 num_clock_tokens=INITIAL_NUM_CLOCK_TOKENS,
                 discard_pile=None):
        # data is a map from color -> cards
        self.cards_on_table = {c: [] for c in HANABI_COLORS}
        self.num_fuse_tokens = num_fuse_tokens
        self.num_clock_tokens = num_clock_tokens
        self.discard_pile = [] if not discard_pile else discard_pile

    def play_card(self, card):
        """ Plays a card on the table, assuming it is valid.

        If not valid, throw exception
        """
        if not self.can_play_card(card):
            self.num_fuse_tokens -= 1
            logger.debug("***BOOM*** Booms left: {}".format(self.num_fuse_tokens))
            self.discard(card)
        else:
            self.cards_on_table[card.color].append(card)
            if card.number == 5:
                if self.num_clock_tokens < INITIAL_NUM_CLOCK_TOKENS:
                    self.num_clock_tokens += 1

                logger.debug("***HANABI!!!*** {} clock tokens".format(self.num_clock_tokens))

    def can_play_card(self, card):
        playable_cards = self.get_playable_cards()
        return card in playable_cards

    def get_playable_cards(self):
        playable_cards = []
        for color, cards in self.cards_on_table.items():
            if len(cards) >= N_CARDS_PER_SUIT:
                continue
            next_number = len(cards) + 1
            playable_cards.append(Card(color, next_number))
        return playable_cards

    def discard(self, card):
        self.discard_pile.append(card)
        self.num_clock_tokens += 1

    def get_score(self):
        numbers_for_colors = ([c.number for c in cards] for cards in list(self.cards_on_table.values()))
        return sum((max(x) if len(x) > 0 else 0 for x in numbers_for_colors))

    def __repr__(self):
        return "Table(cards_on_table={},num_fuse_tokens={},num_clock_tokens={},discard_pile={})".format(self.cards_on_table,self.num_fuse_tokens,
            self.num_clock_tokens, self.discard_pile)

    def show(self):
        print("fuse tokens left: ", self.num_fuse_tokens)
        print("information tokens left: ", self.num_clock_tokens)
        print()
        for color, cards in self.cards_on_table.items():
            row_string = color + ":"
            for card in cards:
                row_string += "\t{}".format(card.number)
            if len(cards) == 0:
                row_string += "\tempty"
            print(row_string)