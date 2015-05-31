from strategies import strategy_22

__author__ = 'julenka'

import argparse
import sys

from strategies.interactive_strategy import  *
from strategies.strategy_1 import *
from strategies.strategy_22 import *

from game import Game

import matplotlib.pyplot as plt
import numpy as np

def testStrategy(strategy):
    # game loop:
    game = Game(3, interactive=True)
    game.strategy = strategy
    score = game.playEntireGame()
    print "final score: ", str(score)

def evaluateStrategy(strategy, n_players, evaluation_times, show_hist=False):

    scores = []
    for i in xrange(evaluation_times):
        game = Game(n_players)
        game.strategy = strategy
        score = game.playEntireGame()
        scores.append(score)

    if(show_hist):
        bins = np.linspace(0,25,26)
        plt.hist(scores, bins)
        plt.show()
    return scores

if __name__ == '__main__':
    parser = argparse.ArgumentParser("evaluate a strategy")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("-n", "--n-players", type=int, default=3, help="number of players")
    parser.add_argument("-r", "--runs", type=int, default=20, help="number of runs to evaluate")
    args = parser.parse_args(sys.argv[1:])


    strategy = Strategy22(0.9)
    if args.test:
        testStrategy(strategy)
    else:
        scores = evaluateStrategy(strategy, args.n_players, args.runs)
        print np.mean(scores)
# testStrategy(InteractiveStrategy())
# testStrategy(PlayZerothStrategy())

# evaluateStrategy(Strategy22(0.7),3)

# mean_scores = []
# for i in xrange(10, 101, 10):
# 	probability = i/100.0
# 	scores = evaluateStrategy(Strategy1(probability), 3)
# 	mean_scores.append((probability, np.mean(scores)))

# print mean_scores

