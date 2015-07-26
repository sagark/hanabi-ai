from deck import Deck
from constants import CARDS_PER_PLAYER
from log import logger
from player import Player
from table import Table

__author__ = 'julenka'

class Game:
    def __init__(self, n_players, interactive=False):
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

        self.interactive = interactive

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

    def _do_turn(self):
        if self.strategy is None:
            raise Exception("doTurn called but no player strategy specified")
        # do the turn
        other_players = [p for i,p in enumerate(self.players) if i != self.cur_player]
        method, params = self.strategy.do_turn(self.cur_player, self.players[self.cur_player].guesses,
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

    def _is_game_over(self):
        """ Check whether game is over

        Ways game can be over:
        deck is empty and n_players moves have been executed


        Returns:
        None if game is not over
        String explaining game over reason is over"""
        self.gameOverReason = None
        if self.num_turns_left is not None and self.num_turns_left == 0:
            self.gameOverReason = "Deck is empty and out of turns"
        if self.table.num_clock_tokens < 0:
            self.gameOverReason = "Tried to use information when no information was left"
        if self.table.num_fuse_tokens <= 0:
            self.gameOverReason = "Explosion when no fuse tokens left"
        if len(self.table.getPlayableCards()) == 0:
            self.gameOverReason = "****YOU GOT A PERFECT SCORE****"
        return self.gameOverReason

    def _game_over(self):
        self._print_header("Game Over")
        print "reason: {}".format(self.gameOverReason)
        print
        print

    def _print_header(self, header):
        separator = "*" * 20
        print
        print separator
        print header
        print separator

    def show(self):
        self._print_header("players")
        for p in self.players:
            print str(p)
        print
        print "Current Player: player {}".format(self.cur_player)

        self._print_header("deck")
        print self.deck

        self._print_header("table")
        self.table.show()

    def play(self):
        """ Plays the entire game assuming a strategy is set

        1. Check if strategy is set
        2. Loop and play game until game is over
        """
        if not self.strategy:
            raise Exception ("playEntireGame called but no strategy was set!")

        while (not self._is_game_over()):
            if self.interactive:
                self.show()
                print "Press enter to view action..."
                raw_input()
            self._do_turn()
            if self.interactive:
                print
                print "Press enter to view new state..."
                raw_input()
        self._game_over()
        return self.table.getScore()