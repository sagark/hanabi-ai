import re
class InteractiveStrategy:
	def doTurn(self, player_num, player_guesses, other_players, table):
		''' Perform a single turn  

		Params:
		player_num -- number of player for current turn
		player_guesses -- guesses for the current player
		other_players -- state of other players

		Returns:
		string representing action

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
		for g in player_guesses:
			print g
		print "other_players:"
		for p in other_players:
			print str(p)
		print "table: ", table
		print "your move, player {}:".format(player_num)
		action = raw_input()
		method, params = re.match(r"(.+)\((.+)\)",action).groups()
		method = method.strip()
		commands = ["sayColor", "sayNumber","discard","play","say"]
		while method not in commands:
			print "Invalid command {}, try one of {}".format(method, commands)
			action = stdin.readline()
			method, params = re.match(r"(.+)\((.+)\)",action).groups()
		return action.strip()
