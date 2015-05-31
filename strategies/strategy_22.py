from collections import defaultdict

__author__ = 'julenka'


class Strategy22:
    def __init__(self, play_risk):
        self.play_risk = play_risk

    # input: playable_cards, player_guesses
    # return: probabilities of match
    def compute_probabilities_of_match(self, playable_cards, player_guesses):
        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        # for each guess, stores the probability of a match
        probabilities_of_match = []
        for i, colors_for_guess, numbers_for_guess in guess_list:
            matching_cards = [x for x in playable_cards if
                              x.number in numbers_for_guess and x.color in colors_for_guess]
            num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
            probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess
            probabilities_of_match.append(probability_of_match)
        return probabilities_of_match

    def compute_probabilities_of_possible_match(self, playable_cards, player_guesses):
        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        # for each guess, stores the probability of a match
        probabilities_of_match = []
        for i, colors_for_guess, numbers_for_guess in guess_list:
            matching_cards = [x for x in playable_cards if
                              any((x.number <= n for n in numbers_for_guess)) and x.color in colors_for_guess]
            num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
            probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess
            probabilities_of_match.append(probability_of_match)
        return probabilities_of_match

    ''' A strategy which always plays the zeroth card in its hand '''

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        #######################################################################
        # Check if you can play a card
        #######################################################################

        # playable cards: [Card(color, number), Card(color, number)]
        playable_cards = table.getPlayableCards()
        color_to_number = {c.color: c.number for c in playable_cards}

        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        # for each guess, stores the probability of a match
        probabilities_of_match = self.compute_probabilities_of_match(playable_cards, player_guesses)
        probabilities_possible_match = self.compute_probabilities_of_possible_match(playable_cards, player_guesses)

        # find index of highest probability
        max_prob = max(probabilities_of_match)

        if max_prob > self.play_risk:
            return "play", probabilities_of_match.index(max_prob)

        if 0.0 in probabilities_possible_match and table.num_clock_tokens < 3:
            return "discard", probabilities_possible_match.index(0.0)


        #######################################################################
        # For each player, compute the info gain giving color and number info
        # for each card
        #######################################################################
        # info_gain -> [(player.index, card.color), (player.index, card.color)]
        # Also compute the info gain for playable cards
        # info_gain_playable -> [(player.index, card.color), (player.index, card.color)]
        info_gain_non_playable = defaultdict(list)
        info_gain_playable = defaultdict(list)

        # probability -> index, info
        info_map4 = defaultdict(list)
        fives = []
        # player, number -> cloned_guesses

        for other_player in other_players:
            # info_gain -> (other_player.index, card.number or card.color)
            other_player_colors = set(card.color for card in other_player.cards)
            other_player_numbers = set(card.number for card in other_player.cards)
            old_probabilities = self.compute_probabilities_of_match(playable_cards, other_player.guesses)

            # compute info gain for all cards and colors
            for color_info in other_player_colors:
                cloned_guesses = [guess.clone() for guess in other_player.guesses]
                for card, guess in zip(other_player.cards, cloned_guesses):
                    if card.color == color_info:
                        guess.setIsColor(color_info)
                    else:
                        guess.setIsNotColor(color_info)

                new_probabilities = self.compute_probabilities_of_match(playable_cards, cloned_guesses)
                info_map4[max(new_probabilities) - max(old_probabilities)].append((other_player.index, color_info))

            for number_info in other_player_numbers:
                cloned_guesses = [guess.clone() for guess in other_player.guesses]
                for card, guess in zip(other_player.cards, cloned_guesses):
                    if card.number == number_info:
                        guess.setIsNumber(number_info)
                    else:
                        guess.setIsNotNumber(number_info)

                new_probabilities = self.compute_probabilities_of_match(playable_cards, cloned_guesses)

                info_map4[max(new_probabilities) - max(old_probabilities)].append((other_player.index, number_info))

        #######################################################################
        # Tell someone else about their cards
        #######################################################################
        if table.num_clock_tokens > 0:
            max_probability4 = max(info_map4.keys())
            if max_probability4 > 0.0:
                # for info in info_map5[max_probability5]:
                # return "say", info_map2[max_probability2]
                possible_info = info_map4[max_probability4]
                total_players = len(other_players) + 1

                possible_info_distance_to_cur = [(a - player_num if a > player_num else a + (total_players - player_num),b)
                                                 for a,b in possible_info]

                p, info = sorted(possible_info_distance_to_cur)[0]
                p = (player_num + p) % total_players
                return "say", (p, info)

            # return "say", info_map2[max_probability]

        #######################################################################
        # Discard the oldest cars
        #######################################################################

        min_prob = min(probabilities_possible_match )
        return "discard", probabilities_possible_match.index(min_prob)