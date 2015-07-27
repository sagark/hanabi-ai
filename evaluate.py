#!/usr/bin/env python

__author__ = 'julenka'

import argparse
import datetime
import sys

import numpy as np

import matplotlib.pyplot as plt

from strategies.strategy_22 import *
from game import Game


def test_strategy(s):
    game = Game(3, interactive=True)
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


def main(argv):
    parser = argparse.ArgumentParser("evaluate a strategy")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("-n", "--n-players", type=int, default=3, help="number of players")
    parser.add_argument("-r", "--runs", type=int, default=20, help="number of runs to evaluate")
    parser.add_argument("--plot", action="store_true", help="plot the results of runs")
    args = parser.parse_args(argv)

    strategy = Strategy22(0.7)
    if args.test:
        test_strategy(strategy)
    else:
        scores = evaluate_strategy(strategy, args.n_players, args.runs)
        print np.mean(scores)
        if args.plot:
            plot_scores(scores)

if __name__ == '__main__':
    main(sys.argv[1:])
