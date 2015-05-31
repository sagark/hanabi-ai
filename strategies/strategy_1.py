from collections import defaultdict

__author__ = 'julenka'


class Strategy1:
    def __init__(self, play_risk=0.5):
        self.play_risk = play_risk

    def doTurn(self, player_num, player_guesses, other_players, table, logger):
        #######################################################################
        # Check if you can play a card
        #######################################################################

        # playable cards: [Card(color, number), Card(color, number)]
        playable_cards = table.getPlayableCards()
        color_to_number = {c.color: c.number for c in playable_cards}

        guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

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