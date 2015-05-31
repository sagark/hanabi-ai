#!/usr/bin/env python

""" Simulates a game of hanabi, allowing for experimentation of different hanabi strategies assuming perfect memory """


# TODO: MAKE COLORS AND MOVES ENUMS OR CONSTANTS

# Globals specific to game
HANABI_COLORS = ["red", "blue", "green", "yellow", "white"]
HANABI_SUIT = [1,1,1,2,2,3,3,4,4,5]
N_CARDS_PER_SUIT = len(set(HANABI_SUIT))
# If there are 2 or 3 players, each player receives 5 cards. If there are 4 or 5 players, each player receives 4 cards.
CARDS_PER_PLAYER = {2:5,3:5,4:4,5:4}

INITIAL_NUM_CLOCK_TOKENS = 8
INITIAL_NUM_FUSE_TOKENS = 3


