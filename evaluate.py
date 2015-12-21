#!/usr/bin/env python
""" Evaluates a particular AI strategy for playing Hanabi

"""
__author__ = 'julenka'

import argparse
import datetime
import sys

import numpy as np

import matplotlib.pyplot as plt

from strategies.strategy_22 import *
from strategies.interactive_strategy import *

from game import Game


def test_strategy(s, n_players):
    game = Game(n_players, interactive=True)
    game.strategy = s
    score = game.play()
    print "final score: ", str(score)


def evaluate_strategy(s, n_players, evaluation_times):
    scores = []
    for i in xrange(evaluation_times):
        game = Game(n_players)
        game.strategy = s
        score = game.play()
        scores.append(score)
    return scores

def plot_scores(scores):
    plt.hist(scores)
    now = datetime.datetime.now()
    plt.title("{}\nmean = {}".format(now.strftime("%B %d, %Y"), np.mean(scores)))
    plt.show()

def print_results(scores):
    print("mean score: {}".format(np.mean(scores)))

def main(argv):
    parser = argparse.ArgumentParser("Evaluate a strategy")
    parser.add_argument("--test", action="store_true",
                        help="If true, run a game only once and show result at every turn")
    parser.add_argument("-n", "--n-players", type=int, default=3, help="Number of players")
    parser.add_argument("-r", "--runs", type=int, default=20,
                        help="Number of runs to evaluate. Ignored if test is true")
    parser.add_argument("--plot", action="store_true", help="Plot the results of runs.")
    parser.add_argument("--strategy-string", default="Strategy22(0.7)",
                        help="Strategy constructor string. Strategy should be in package strategies, and "
                             "imported in this script.")

    args = parser.parse_args(argv)

    strategy = eval(args.strategy_string)
    if args.test:
        test_strategy(strategy, args.n_players)
    else:
        scores = evaluate_strategy(strategy, args.n_players, args.runs)
        if args.plot:
            plot_scores(scores)
        print_results

if __name__ == '__main__':
    main(sys.argv[1:])
