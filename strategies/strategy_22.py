from collections import defaultdict

__author__ = 'julenka'
import strategy_utils
import numpy as np
from log import logger
class Strategy22:
    def __init__(self, play_risk):
        self.play_risk = play_risk

    ''' A strategy which always plays the zeroth card in its hand '''

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        #######################################################################
        # Check if you can play a card
        #######################################################################

        # playable cards: [Card(color, number), Card(color, number)]
        playable_cards = table.getPlayableCards()

        # for each guess, stores the probability of a match
        probabilities_of_match = strategy_utils.compute_probabilities_of_match(playable_cards, player_guesses)

        # find index of highest probability
        max_prob = max(probabilities_of_match)

        if max_prob >= self.play_risk:
            return "play", probabilities_of_match.index(max_prob)

        # if 0.0 in probabilities_of_match:
        #     logger.debug("0 in probabilities of match!!!!")
        #     return "discard", probabilities_of_match.index(0.0)


        #######################################################################
        # Tell someone else about their cards
        #######################################################################
        if table.num_clock_tokens > 0:

            info_gain_for_action = strategy_utils.get_info_gain_for_action(other_players, playable_cards, self.play_risk)

            best_action_info_gain = max(info_gain_for_action.keys())
            if best_action_info_gain > 0.0:
                possible_info = info_gain_for_action[best_action_info_gain]
                total_players = len(other_players) + 1

                possible_info_distance_to_cur = [(a - player_num if a > player_num else a + (total_players - player_num),b)
                                                 for a,b in possible_info]

                p, info = sorted(possible_info_distance_to_cur)[0]
                p = (player_num + p) % total_players
                return "say", (p, info)

        #######################################################################
        # Discard the least likely cards
        #######################################################################

        min_prob = min(probabilities_of_match )
        return "discard", probabilities_of_match.index(min_prob)