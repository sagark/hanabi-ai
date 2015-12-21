from deck import Deck
from constants import CARDS_PER_PLAYER
from log import logger
from player import Player
from table import Table

""" Manages the state of a Hanabi game """
__author__ = 'julenka'

class Game:
    def __init__(self, n_players, interactive=False):
        """ Build game of Hanabi. Make the deck, draw cards

        Args:
        n_players: How many players
        interactive: If true, shows the state of game to console at every turn
        """
        if n_players not in CARDS_PER_PLAYER:
            raise Exception("Num players must be between 2 and 5")
        self.deck = Deck()
        self.players = []

        # Game is over is num fuse or num clock tokens goes below zero
        self.cur_player = 0

        self.interactive = interactive

        self.table = Table()
        self.num_turns_left = None
        for i in xrange(n_players):
            self.players.append(Player(self.deck.draw_cards(CARDS_PER_PLAYER[n_players]), "player {}".format(i), i))

    def say(self, idx, param):
        """ Give a piece of information to a player

        :param idx: The index of the player receiving hteinformation
        :param param:  The information being received (either a color or a number)
        :return: None
        """
        try:
            number = int(param)
            self.players[idx].receive_number_info(number)
        except ValueError:
            self.players[idx].receive_color_info(param)

        self.table.num_clock_tokens -= 1

    def _do_discard(self, cur_player_object, idx):
        logger.debug("{} discarding {}".format(cur_player_object.name, cur_player_object.cards[idx]))
        cur_player_object.discard(idx, self.table)
        cur_player_object.draw_card(self.deck)

    def _do_play_card(self, cur_player_object, idx):
        logger.debug("{} playing {}".format(cur_player_object.name, cur_player_object.cards[idx]))
        cur_player_object.play(idx, self.table)
        cur_player_object.draw_card(self.deck)

    def _do_say(self, cur_player_object, params):
        idx, arg = params
        if self.table.num_clock_tokens == 0:
            raise Exception("player {} called 'say' with no information tokens left".format(self.cur_player))
        if idx == self.cur_player:
            raise Exception("player {} is trying to tell itself information".format(idx))
        # TODO: you can never give information about 0 cards. Throw exception
        logger.debug("{} saying {},{}".format(cur_player_object.name, idx, arg))
        self.say(idx, arg)

    def _do_turn(self):
        """ Execute a single turn in the game

        :return:
        """
        if self.strategy is None:
            raise Exception("doTurn called but no player strategy specified")
        # do the turn
        other_players = [p for i, p in enumerate(self.players) if i != self.cur_player]
        cur_player_object = self.players[self.cur_player]
        method, params = self.strategy.do_turn(self.cur_player,
                                               cur_player_object.guesses,
                                               other_players,
                                               self.table,
                                               logger)

        if method == "discard":
            self._do_discard(cur_player_object, int(params))
        elif method == "play":
            self._do_play_card(cur_player_object, int(params))
        elif method.startswith("say"):
            self._do_say(cur_player_object, params)
        else:
            raise Exception("Invalid command returned from strategy.doTurn: {}", method)

        # check if deck is empty, if so, don't draw, instead start countdown
        if self.deck.is_empty():
            if self.num_turns_left is None:
                self.num_turns_left = len(self.players)
            else:
                self.num_turns_left -= 1

        self.cur_player += 1
        self.cur_player %= len(self.players)

    def _is_game_over(self):
        """ Check whether game is over

        Ways game can be over:
        deck is empty and n_players moves have been executed


        :return: None if game is not over, or string explaining game over reason is over"""
        self.gameOverReason = None
        if self.num_turns_left is not None and self.num_turns_left == 0:
            self.gameOverReason = "Deck is empty and out of turns"
        if self.table.num_clock_tokens < 0:
            self.gameOverReason = "Tried to use information when no information was left"
        if self.table.num_fuse_tokens <= 0:
            self.gameOverReason = "Explosion when no fuse tokens left"
        if len(self.table.get_playable_cards()) == 0:
            self.gameOverReason = "****YOU GOT A PERFECT SCORE****"
        return self.gameOverReason

    def _game_over(self):
        """ Print a game over message

        :return:
        """
        self._print_header("Game Over")
        print "reason: {}".format(self.gameOverReason)
        print
        print

    def _print_header(self, header):
        """ Print a header message

        :param header:
        :return:
        """
        separator = "*" * 20
        print
        print separator
        print header
        print separator

    def show(self):
        """ Print the state of the game to the console

        :return:
        """
        self._print_header("Current Player: {}".format(self.cur_player))
        self._print_header("Players")
        for p in self.players:
            print str(p)
            print
        print

        self._print_header("Deck")
        print self.deck

        self._print_header("Table")
        self.table.show()

    def play(self):
        """ Plays the entire game assuming a strategy is set

        1. Check if strategy is set
        2. Loop and play game until game is over
        """
        if not self.strategy:
            raise Exception("playEntireGame called but no strategy was set!")

        while not self._is_game_over():
            if self.interactive:
                self.show()
                print "Press enter to view action, or q to quit..."
                user_input = raw_input()
                if user_input == "q":
                    import sys
                    sys.exit(1)
            self._do_turn()
            if self.interactive:
                print
                print "Press enter to view new state..."
                raw_input()
        self._game_over()
        return self.table.get_score()
