import re

from hanabi import HANABI_COLORS as HANABI_COLORS

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
		for i,g in enumerate(player_guesses):
			print i, g
		print "other_players:"
		for p in other_players:
			print str(p)
		print "table: ", table
		print "your move, player {}:".format(player_num)
		commands = ["sayColor", "sayNumber","discard","play","say"]
		validPlay = False
		errorMessage = None
		while not validPlay:
			validPlay = True
			if errorMessage:
				print errorMessage 
			action = raw_input()	
			match = re.match(r"(.+)\((.+)\)",action)
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
	for i,g in enumerate(player_guesses):
		print i, g
	print "other_players:"
	for p in other_players:
		print str(p)
	print "table: ", table

class PlayZerothStrategy:
	''' A strategy which always plays the zeroth card in its hand '''
	def doTurn(self, player_num, player_guesses, other_players, table, logger):
		return "play", 0


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

		guess_list = [(i,g.possible_colors, g.possible_numbers) for i,g in enumerate(player_guesses)]
	
		for i, colors_for_guess, numbers_for_guess in guess_list:					
			# there is only one number
			# A possible card matches if its number matches the guessed number AND its color is one of the possible colors
			matching_cards = [ x for x in playable_cards if x.number in numbers_for_guess and x.color in colors_for_guess ]
			num_possible_cards_for_guess = len(colors_for_guess) * len(numbers_for_guess)
			probability_of_match = float(len(matching_cards)) / num_possible_cards_for_guess
			if probability_of_match >= self.play_risk:
				return "play", i


		#######################################################################
		# Tell someone else about their cards
		#######################################################################
		if table.num_clock_tokens > 0:
			for other_player in other_players:
				for card, guess in zip(other_player.cards, other_player.guesses):
					if card in playable_cards:
						# check if the player alrady knows about it
						colors_for_card = guess.possible_colors
						numbers_for_card = guess.possible_numbers
						if len(colors_for_card) > 1:
							return "say", (other_player.index, card.color)
						if len(numbers_for_card) > 1:
							return "say", (other_player.index, card.number)


		#######################################################################
		# Discard the oldest card 
		#######################################################################
		return "discard", 0
