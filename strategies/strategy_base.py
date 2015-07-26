#!/usr/bin/env python
# coding=utf-8
""" Contains base class for Strategy
"""
__author__ = 'julenka'


class Strategy:
    """ All strategies should override this class like so:

    class MyStrategy(Strategy)

    """

    def __init__(self):
        raise NotImplementedError

    def do_turn(self, player_num, player_guesses, other_players, table, logger):
        raise NotImplementedError
