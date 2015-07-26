__author__ = 'julenka'
from collections import defaultdict
# input: playable_cards, player_guesses
# return: probabilities of match
def compute_probabilities_of_match(playable_cards, player_guesses):
    guess_list = [(i, g.possible_colors, g.possible_numbers) for i, g in enumerate(player_guesses)]

    # for each guess, stores the probability of a match
    probabilities_of_match = []
    for i, colors_for_guess, numbers_for_guess in guess_list:
        matching_cards = [x for x in playable_cards if
                          x.number in numbers_for_guess and x.color in colors_for_guess]
        num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
        probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess if num_possible_cards_for_guess > 0 else 0
        probabilities_of_match.append(probability_of_match)
    return probabilities_of_match


def get_info_gain_for_action(other_players, playable_cards, risk):
    """
    # info_gain -> [(player.index, card.color), (player.index, card.color)]
    # Also compute the info gain for playable cards
    # info_gain_playable -> [(player.index, card.color), (player.index, card.color)]

    :param other_players:
    :param playable_cards:
    :return:
    """
    player_to_info_gain_for_card = defaultdict(list)
    # player, number -> cloned_guesses

    for other_player in other_players:
        # info_gain -> (other_player.index, card.number or card.color)
        other_player_colors = set(card.color for card in other_player.cards)
        other_player_numbers = set(card.number for card in other_player.cards)
        old_probabilities = compute_probabilities_of_match(playable_cards, other_player.guesses)

        # compute info gain for all cards and colors
        for info in other_player_colors | other_player_numbers:

            cloned_guesses = [guess.clone() for guess in other_player.guesses]

            for card, guess in zip(other_player.cards, cloned_guesses):
                if isinstance(info, str):
                    if card.color == info:
                        guess.setIsColor(info)
                    else:
                        guess.setIsNotColor(info)
                else:
                    if card.number == info:
                        guess.setIsNumber(info)
                    else:
                        guess.setIsNotNumber(info)

            new_probabilities = compute_probabilities_of_match(playable_cards, cloned_guesses)

            player_to_info_gain_for_card[max(new_probabilities) - max(old_probabilities)].append((other_player.index, info))

    return player_to_info_gain_for_card
