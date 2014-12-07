import re
from collections import defaultdict


class InteractiveStrategy:
    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        ''' Perform a single turn

        Params:
        player_num -- number of player for current turn
        player_guesses -- guesses for the current player
        other_players -- list of Player objects, with state of other players

        Player Object fields:
        cards = cards
        guesses = [Guess() for c in self.cards]
        name -- player name
        index -- index of player (use to refer in 'say')

        Returns:
        (method, params) tuple
        method - one of ["sayColor", "sayNumber","discard","play","say"]
        params - if method is "play" or "discard", then a single int representing the card to players
        otherwise, (player_index, color or number tuple)

        Possible Actions:
        sayColor(player_num, color)
        sayNumber(play_num, num)
        discard(index)
        play(index)
        '''
        print
        print "*" * 80
        print
        print "player_guesses:"
        for i, g in enumerate(player_guesses):
            print i, g
        print "other_players:"
        for p in other_players:
            print str(p)
        print "table: ", table
        print "your move, player {}:".format(player_num)
        commands = ["sayColor", "sayNumber", "discard", "play", "say"]
        validPlay = False
        errorMessage = None
        while not validPlay:
            validPlay = True
            if errorMessage:
                print errorMessage
            action = raw_input()
            match = re.match(r"(.+)\((.+)\)", action)
            if not match:
                validPlay = False
                errorMessage = "Invalid command format. Should be command(args)"
                continue
            method, params = match.groups()
            if method not in commands:
                validPlay = False
                errorMessage = "Invalid command {}, try one of {}".format(method, commands)
            if method in ["play", "discard"]:
                try:
                    n = int(params)
                    if n < 0 or n >= len(player_guesses):
                        errorMessage = "Argument to {} must be >=0 and < {}".format(method, len(player_guesses))
                        validPlay = False
                    else:
                        return method, n
                except ValueError:
                    validPlay = False
                    errorMessage = "Argument to {} must be int, was {}".format(method, params)
            else:
                # this is a "say" command
                idx, param = params.split(',')
                try:
                    idx = int(idx)
                except ValueError:
                    validPlay = False
                    errorMessage = "Argument to {} must of form (player_index, info)".format(method)
                return method, (idx, param)


def printState(player_num, player_guesses, other_players, table, logger):
    print
    print "*" * 80
    print "player {}".format(player_num)
    print "*" * 80
    print
    print "player_guesses:"
    for i, g in enumerate(player_guesses):
        print i, g
    print "other_players:"
    for p in other_players:
        print str(p)
    print "table: ", table


class PlayZerothStrategy:
    ''' A strategy which always plays the zeroth card in its hand '''

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        return "play", 0


class Strategy22:
    def __init__(self, play_risk, print_state=False):
        self.play_risk = play_risk
        self.print_state = print_state

    # input: playable_cards, player_guesses
    # return: probabilities of match
    def compute_probabilities_of_match(self, playable_cards, player_guesses):
        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        # print playable_cards
        # for each guess, stores the probability of a match
        probabilities_of_match = []
        for i, colors_for_guess, numbers_for_guess in guess_list:
            matching_cards = [x for x in playable_cards if
                              x.number in numbers_for_guess and x.color in colors_for_guess]
            num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
            probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess
            probabilities_of_match.append(probability_of_match)
        return probabilities_of_match

    ''' A strategy which always plays the zeroth card in its hand '''

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        # print the game state
        if self.print_state:
            printState(player_num, player_guesses, other_players, table, logger)

        #######################################################################
        # Check if you can play a card
        #######################################################################

        # playable cards: [Card(color, number), Card(color, number)]
        playable_cards = table.getPlayableCards()
        color_to_number = {c.color: c.number for c in playable_cards}

        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        # print playable_cards
        # for each guess, stores the probability of a match
        probabilities_of_match = self.compute_probabilities_of_match(playable_cards, player_guesses)
        for i, colors_for_guess, numbers_for_guess in guess_list:
            matching_cards = [x for x in playable_cards if
                              x.number in numbers_for_guess and x.color in colors_for_guess]
            if len(matching_cards) > 0 and (
                                len(colors_for_guess) == 1 and matching_cards[0].color == colors_for_guess[0] or len(
                            numbers_for_guess) == 1 and matching_cards[0].number == numbers_for_guess[0]):
                return "play", i
        # find index of highest probability
        max_prob = max(probabilities_of_match)

        if max_prob > self.play_risk:
            return "play", probabilities_of_match.index(max_prob)


        #######################################################################
        # For each player, compute the info gain giving color and number info
        # for each card
        #######################################################################
        # info_gain -> [(player.index, card.color), (player.index, card.color)]
        # Also compute the info gain for playable cards
        # info_gain_playable -> [(player.index, card.color), (player.index, card.color)]
        info_gain_non_playable = defaultdict(list)
        info_gain_playable = defaultdict(list)

        # (player, info) -> maximum of likelihood for hand
        info_map1 = {}
        info_map2 = {}
        info_map3 = {}
        info_map4 = {}
        info_map5 = defaultdict(list)

        fives = []
        # player, number -> cloned_guesses
        dbg1 = {}

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
                info_map1[(other_player.index, color_info)] = sum(new_probabilities)
                info_map2[sum(new_probabilities)] = (other_player.index, color_info)
                info_map3[max(new_probabilities)] = (other_player.index, color_info)
                info_map4[max(new_probabilities) - max(old_probabilities)] = (other_player.index, color_info)

                info_gain = 0
                for i, p in enumerate(old_probabilities):
                    g = other_player.guesses[i]
                    if len(g.possible_colors) == 1 or len(g.possible_numbers) == 1:
                        continue

                    info_gain += (new_probabilities[i] - p)

                info_map5[sum(new_probabilities) - sum(old_probabilities)].append((other_player.index, color_info))
            # info_map5[info_gain] = (other_player.index, color_info)
            for number_info in other_player_numbers:
                cloned_guesses = [guess.clone() for guess in other_player.guesses]
                for card, guess in zip(other_player.cards, cloned_guesses):
                    if card.number == number_info:
                        guess.setIsNumber(number_info)
                    else:
                        guess.setIsNotNumber(number_info)

                new_probabilities = self.compute_probabilities_of_match(playable_cards, cloned_guesses)
                dbg1[(other_player.index, number_info)] = (cloned_guesses, new_probabilities)
                info_map1[(other_player.index, number_info)] = sum(new_probabilities)
                info_map2[sum(new_probabilities)] = (other_player.index, number_info)
                info_map3[max(new_probabilities)] = (other_player.index, number_info)
                info_map4[max(new_probabilities) - max(old_probabilities)] = (other_player.index, number_info)

                info_gain = 0
                for i, p in enumerate(old_probabilities):
                    g = other_player.guesses[i]
                    if len(g.possible_colors) == 1 or len(g.possible_numbers) == 1:
                        continue

                    info_gain += (new_probabilities[i] - p)

                info_map5[sum(new_probabilities) - sum(old_probabilities)].append((other_player.index, number_info))
            # info_map5[info_gain] = (other_player.index, number_info)

            # for k,v in dbg1.iteritems():
            # print k
            # 	guesses, prob = v
            # 	for g in guesses:
            # 		print "\t", g, "\t"
            # 	print "\t", prob
            # for card, guess in zip(other_player.cards, other_player.guesses):
            # 	if card.color in color_to_number and color_to_number[card.color] < card.number:
            # 		continue
            # 	colors_for_card = guess.possible_colors
            # 	numbers_for_card = guess.possible_numbers

            # 	info_gain_color = (len(colors_for_card) - 1) * len(numbers_for_card)
            # 	info_gain_number = (len(numbers_for_card) - 1) * len(numbers_for_card)

            # 	if card in playable_cards:
            # 		info_gain_playable[info_gain_number].append( (other_player.index, card.number) )
            # 		info_gain_playable[info_gain_color].append( (other_player.index, card.color) )
            # 	elif card.number == 5:
            # 		fives.append(other_player.index, card.number)
            # 	else:
            # 		info_gain_non_playable[info_gain_number].append( (other_player.index, card.number) )
            # 		info_gain_non_playable[info_gain_color].append( (other_player.index, card.color) )


        #######################################################################
        # Tell someone else about their cards
        #######################################################################
        # if table.num_clock_tokens > 0:
        # if len(info_gain_playable) > 0:
        # 		playable_max = max(info_gain_playable.keys())
        # 		return "say", info_gain_playable[playable_max][0]
        # 	elif len(fives) > 0:
        # 		return "say", fives[0]
        # 	elif table.num_clock_tokens > 2 and len(info_gain_non_playable) > 0:
        # 		playable_max = max(info_gain_non_playable.keys())
        # 		return "say", info_gain_non_playable[playable_max][0]
        print "info_map2", info_map2
        print "info_map3", info_map3
        if table.num_clock_tokens > 0:
            max_probability2 = max(info_map2.keys())
            max_probability3 = max(info_map3.keys())
            max_probability4 = max(info_map4.keys())
            max_probability5 = max(info_map5.keys())
            # if max_probability3 >= self.play_risk:
            if max_probability5 >= 0.0:
                # for info in info_map5[max_probability5]:
                # return "say", info_map2[max_probability2]
                return "say", info_map5[max_probability5][0]
            # return "say", info_map2[max_probability]

        #######################################################################
        # Discard the oldest cars
        #######################################################################
        possible_discard_indices = range(len(player_guesses))
        # for i, colors_for_guess, numbers_for_guess in guess_list:
        # 	if numbers_for_guess[0] == 5 and len(possible_discard_indices) > 0:
        # 		del possible_discard_indices[i]
        return "discard", possible_discard_indices[0]


class Strategy1:
    def __init__(self, play_risk):
        self.play_risk = play_risk

    ''' A strategy which always plays the zeroth card in its hand '''

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        # print the game state
        printState(player_num, player_guesses, other_players, table, logger)

        #######################################################################
        # Check if you can play a card
        #######################################################################

        # playable cards: [Card(color, number), Card(color, number)]
        playable_cards = table.getPlayableCards()
        color_to_number = {c.color: c.number for c in playable_cards}
        print color_to_number

        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

        print playable_cards
        for i, colors_for_guess, numbers_for_guess in guess_list:
            matching_cards = [x for x in playable_cards if
                              x.number in numbers_for_guess and x.color in colors_for_guess]
            num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
            probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess
            if probability_of_match >= self.play_risk:
                return "play", i
            if len(matching_cards) > 0 and (
                                len(colors_for_guess) == 1 and matching_cards[0].color == colors_for_guess[0] or len(
                            numbers_for_guess) == 1 and matching_cards[0].number == numbers_for_guess[0]):
                return "play", i


        #######################################################################
        # For each player, compute the info gain giving color and number info
        # for each card
        #######################################################################
        # info_gain -> [(player.index, card.color), (player.index, card.color)]
        # Also compute the info gain for playable cards
        # info_gain_playable -> [(player.index, card.color), (player.index, card.color)]
        info_gain_non_playable = defaultdict(list)
        info_gain_playable = defaultdict(list)
        fives = []
        for other_player in other_players:
            for card, guess in zip(other_player.cards, other_player.guesses):
                if card.color in color_to_number and color_to_number[card.color] < card.number:
                    continue
                colors_for_card = guess.possible_colors
                numbers_for_card = guess.possible_numbers

                info_gain_color = (len(colors_for_card) - 1) * len(numbers_for_card)
                info_gain_number = (len(numbers_for_card) - 1) * len(numbers_for_card)

                if card in playable_cards:
                    info_gain_playable[info_gain_number].append((other_player.index, card.number))
                    info_gain_playable[info_gain_color].append((other_player.index, card.color))
                elif card.number == 5:
                    fives.append(other_player.index, card.number)
                else:
                    info_gain_non_playable[info_gain_number].append((other_player.index, card.number))
                    info_gain_non_playable[info_gain_color].append((other_player.index, card.color))


        #######################################################################
        # Tell someone else about their cards
        #######################################################################
        if table.num_clock_tokens > 0:
            if len(info_gain_playable) > 0:
                playable_max = max(info_gain_playable.keys())
                return "say", info_gain_playable[playable_max][0]
            elif len(fives) > 0:
                return "say", fives[0]
            elif table.num_clock_tokens > 2 and len(info_gain_non_playable) > 0:
                playable_max = max(info_gain_non_playable.keys())
                return "say", info_gain_non_playable[playable_max][0]

        #######################################################################
        # Discard the oldest cars
        #######################################################################
        possible_discard_indices = range(len(player_guesses))
        for i, colors_for_guess, numbers_for_guess in guess_list:
            if numbers_for_guess[0] == 5:
                del possible_discard_indices[i]
        return "discard", possible_discard_indices[0]
