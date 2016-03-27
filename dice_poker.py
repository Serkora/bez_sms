import numpy as np
import itertools

COMBINATIONS = ["High", "Pair", "Two pairs", "Three of a kind", "Small straight",
				"Big straight", "Even", "Odd", "Full house", "Four of a kind", "Poker"]

class Table(object):
	def __init__(self, players, ai_seats, small_blind=2, imaginary=False, imaginator=None):
		self.imaginary=imaginary
		self.imaginator=imaginator
		self.players = self.generate_players(players, ai_seats)
		self.turns = ['preflop', 'flop']
		self.dealer = -1
		self.small_blind = small_blind
		self.round_pot = 0
		self.turn_pot = 0
		self.max_bet = 0
		self.dice = None
	
	def play_round(self):
		self._print("------------------\nNew Round!")
		for turn in self.turns:
			self.start_turn(turn)
			self.make_turn(turn)
			winners = self.end_turn(turn)
			if winners:
				return winners
	
	def _print(self, *args):
		# will be used to render the text in gui later
		if self.imaginary: return
		print(*args)
	
	def generate_players(self, players, ai_seats):
		plrs = []
		for seat in range(players):
			player = Player(self, seat, seat in ai_seats)
			if self.imaginary and seat == self.imaginator.seat:
				player.imaginator = True
			plrs.append(player)
		return plrs
	
	def update(self, cycle=False):
		self.max_bet = max(p.bet for p in self.players)
		self.turn_pot = sum(p.bet for p in self.players)
		if len(self.get_info()[0]) == 1:
			return True
		bets = (p.bet for p in self.players if p.active)
		if len(set(bets)) == 1 and cycle:
			return True
	
	def get_info(self):
# 		return ("Active players: %d, Dice: %s, Pot: %d, Max bet: %d" % (
# 			len(self.players), str(self.dice), self.pot, self.max_bet))
		active = [p for p in self.players if p.active]
		return active, str(self.dice), self.round_pot + self.turn_pot, self.max_bet
	
	def print_move(self, player, move):
		name = "Player %d" % player.seat
		if move == "Fold":
			text = "%s folded" % name
		elif move == "Check":
			text = "%s checked" % name
		elif move == "Call":
			text = "%s called %d coins" % (name, self.max_bet)
		elif move[0] == "Bet":
			text = "%s bet %d coins" % (name, move[1])
		elif move[0] == "Raise":
			text = "%s raised %d coins" % (name, move[1])
		
		self._print(text)
	
	def rotate_dealer(self):
		self.dealer = (self.dealer + 1) % len(self.players)
		if not self.imaginary:
			self._print("Player %d is the dealer" % self.dealer)
	
	def deal_dice(self):
		for player in self.players:
			player.dice = tuple(np.random.choice(range(1,7),2))	
			if self.imaginary and player.seat == self.imaginator.seat:
				player.dice = self.imaginator.dice
	
	def blinds(self):
		self.players[(self.dealer + 1) % len(self.players)].make_bet(self.small_blind)
		self.players[(self.dealer + 2) % len(self.players)].make_bet(self.small_blind * 2)
	
	def start_turn(self, turn):
		self._print(" === Starting turn %s ===" % turn)
		if turn == "preflop":
			self.dice = None
			self.round_pot = 0
			self.turn_pot = 0
			self.max_bet = 0
			for player in self.players: 
				player.bet = 0 
				player.active = True
			if not self.imaginary:
				self.rotate_dealer()
			self.blinds()
			self.deal_dice()
		elif turn == "flop":
			if self.imaginary and self.dice: return
			self.dice = tuple(np.random.choice(range(1,7),5))
	
	def make_turn(self, turn):
		cycle = False
		first = (self.dealer + 3) % len(self.players)
		i = first
# 		print("first: ", first, "len players: ", len(self.players))
		self.update()
		while True:
# 			print("making turn %s" % turn)
# 			print("player %d is making a move, active players: %d" % (i, len([p for p in self.players if p.active])))
			if self.players[i].active:
				move = self.players[i].turn(self, turn)
				self.print_move(self.players[i], move)
# 			print("players: ", len(self.players))
			i = (i + 1) % len(self.players)
			if i == first:
				cycle = True
			if self.update(cycle):
				break
	
	def end_turn(self, turn):
		for player in self.players:
			player.bet = 0
		self.max_bet = 0
		self.round_pot += self.turn_pot
		self.turn_pot = 0

		active = self.get_info()[0]
		if len(active) == 1:
			self._print("%s has won %d coins!" % (active[0].get_name(), self.round_pot))
			active[0].stack += self.round_pot
			return (active[0].seat,)

		if turn == "flop":
			highest = ((None, (-1, (0,0,0,0,0))),)		# ((player, best_hand), )
			i = 0
			for player in self.players:
				if not player.active:
					continue
				best_hand = player.calculate_hand_score(self.dice)
				self._print("Player %s best hand: %s, dice: " % (player.seat, 
					COMBINATIONS[best_hand[0]]), best_hand)
				if best_hand[0] > highest[0][1][0]:
					highest = ((player, best_hand),)
				elif best_hand[0] == highest[0][1][0]:
					cmp = player.compare_same_combination(best_hand[0], best_hand[1], highest[0][1][1])
					if cmp == 1:
						highest = ((player, best_hand),)
					elif cmp == 0:
						highest += ((player, best_hand),)
			
			if len(highest) == 1:
				self._print("%s won %d coins with %s, dice: " % (highest[0][0].get_name(), 
					self.round_pot, COMBINATIONS[highest[0][1][0]]), highest[0][1][1])
				highest[0][0].stack += self.round_pot
				winners = (highest[0][0].seat,)
			else:
				split = self.round_pot // len(highest)
				self._print("Several players won %d coins each: " % split, highest)
				for e in highest:
					e[0].stack += split
					
				# not exactly correct, but at least no money disappear
				highest[0][0].stack += self.round_pot % len(highest)
				
				winners = tuple(e[0].seat for e in highest)
			return winners
	

class Player(object):
	def __init__(self, table, seat, ai=False, stack=50):
		self.table = table
		self.seat = seat
		self.ai = ai
		self.dice = (0,0)
		self.stack = stack
		self.bet = 0
		self.active = True
		self.funcs = [self.make_fold, self.make_check, self.make_call, self.make_bet, self.make_raise]
		self.imaginator = False
	
	def __repr__(self):
		text = "AI " if self.ai else "Human "
		text += "player at seat %d. " % self.seat
		text += "Dice: %d, %d" % (self.dice)
		return text

	def get_name(self):
		return "Player %d (%s)" % (self.seat, "AI" if self.ai else "Human")

	def make_fold(self):
		self.active = False
		return "Fold"

	def make_check(self):
		pass
		return "Check"

	def make_call(self):
		self.make_bet(self.table.max_bet)
		return "Call"

	def make_bet(self, value=None):
		if value is None:
			value = self.table.small_blind * 2
		self.stack -= (value - self.bet)
		self.bet = value
		return "Bet", value

	def make_raise(self, value=None):
		if value is None:
			value = self.table.small_blind * 4
		self.make_bet(value)
		return "Raise", value

	def calculate_hand_score(self, dice):
		if len(dice) < 3:
			raise ValueError("Can't calculate hand score with less than 5 dice!")
		elif self.dice == (0,0):
			raise ValueError("Can't caluclate hand score without own dice!")
		flop_combinations = itertools.permutations(dice, 3)
		best_hand = (-1, ())
		for flop_three in flop_combinations:
			cmb = self.dice + flop_three
			score = self.calculate_combination_score(cmb)
			if score > best_hand[0] or (score == best_hand[0] and 
					self.compare_same_combination(score, cmb, best_hand[1]) == 1):
				best_hand = (score, cmb)
		return best_hand
		
	def calculate_combination_score(self, dice):
		""" Combinations score:
		high - 0; pair - 1; two pairs - 2; three of kind - 3;
		mali straight - 4; bolsho straight - 5; even - 6; 
		odd - 7; full house - 8; four of a kind - 9; poker - 10;
		""" 
		if len(dice) != 5:
			raise ValueError("Can only get the combination score of exactly 5 dice")
		dice_set = set(dice)
		dice_sorted = sorted(dice)
		dice_set_sorted = sorted(dice_set)
		
		if len(dice_set) == 1:		# (a,a,a,a,a)
			# poker
			return 10
		elif len(dice_set) == 2:	# (a,a,b,b,b), (a,a,a,b,b), (a,b,b,b,b), (a,a,a,a,b)
			# four of a kind or full house
# 			if len(set(dice_sorted[1::2])) == 1:
			if dice_sorted[1] == dice_sorted[3]:
				return 9			# if elements 1 and 3 are equal, then four of a kind
			else:
				return 8			# otherwise just a full house
		elif len(dice_set) == 3:
			# odd or even
			s = sum(map(lambda x: x%2, dice))		
			if s == 5:
				return 7			# all elements are odd
			elif s == 0:
				return 6			# all elements are even
			# three of a kind or two pairs
				# (a,a,b,b,c), (a,a,b,c,c), (a,b,b,c,c)
				# (a,a,a,b,c), (a,b,b,b,c), (a,b,c,c,c)
			ds = dice_sorted
			if ds[0] == ds[2] or ds[1] == ds[3] or ds[2] == ds[4]:
				return 3			# three of a kind
			else:
				return 2			# two pairs
		elif len(dice_set) == 4:
			# mali straight or pair
 			# (1,1,2,3,4), (1,2,2,3,4), (1,2,3,3,4), (1,2,3,4,4),
 			# (2,2,3,4,5), (2,3,3,4,5), (2,3,4,4,5), (2,3,4,5,5)
 			# (3,3,4,5,6), (3,4,4,5,6), (3,4,5,5,6), (3,4,5,6,6)
 			
 			# (1,2,3,4), (2,3,4,5), (3,4,5,6)
			if dice_set_sorted[3] - dice_set_sorted[0] == 3:
				return 4			# mali straight
			else:
				return 1			# pair
		elif len(dice_set) == 5:
			# bolsho straight, mali straight or high
			if dice_sorted == [1,2,3,4,6] or dice_sorted == [1,3,4,5,6]: # fuck that shit
				return 4			# mali straight
			elif dice_sorted[4] - dice_sorted[0] == 4:
				return 5			# bolsho straight
			else:
				return 0			# high
		else:
			raise TypeError("wtf...")
	
	def compare_same_combination(self, score, c1, c2):
		# score - 1-10 value of the combination.
		c1 = sorted(c1)
		c2 = sorted(c2)

		if score in (0, 5, 6, 7, 10):
			v1 = max(c1)			# only the highest dice matters because
			v2 = max(c2)			# all 5 are involved in the combination
		elif score in (1, 2, 3, 9):
			c1_pairs = set(x[0] for x in zip(c1,c1[1:]) if x[0]==x[1])
			c2_pairs = set(x[0] for x in zip(c2,c2[1:]) if x[0]==x[1])
			v1 = max(c1_pairs)		# highest value of the paired dice matters
			v2 = max(c2_pairs)
		elif score == 8:
			v1 = c1[2]				# middle dice is from the set part of the full house
			v2 = c1[2]
		elif score == 4:
			ds1 = sorted(set(c1))
			ds2 = sorted(set(c2))
			v1 = ds1[3]
			v2 = ds2[3]

		if v1 > v2: 
			return 1
		elif v1 == v2: 
			return 0
		else: 
			return -1
		
	def get_choices(self, table):
		# not pretty yet
		choices = {0: "Fold", 1: "Check", 2: "Call %d" % table.max_bet, 3: "Bet bb", 4: "raise to 2 bb"}
# 		if self.imaginator:
# 			choices.pop(0)

		if self.bet != table.max_bet:
			choices.pop(1)
		else:
			choices.pop(2)

		if table.max_bet != 0:
			choices.pop(3)
		if table.max_bet == table.small_blind * 4:
			choices.pop(4)
		return choices
	
	def turn(self, table, turn):
		# turn is "preflop" or "flop"
		if not self.active:
			return False

		if self.ai:
			return self._ai_turn(table, turn)
		else:
			return self._human_turn(table, turn)
	
	def _ai_turn(self, table, turn):
		if table.imaginary:
			choices = self.get_choices(table)
			choice = np.random.choice(list(choices.keys()))
			return self.funcs[choice]()
		else:
			# imagine a table, do monte-carlo stuff
			print("AI turn")
			wins = 0
			iters = 100
			im_table = Table(len(table.players), range(len(table.players)), imaginary=True, imaginator=self)
			im_table.turns = im_table.turns[im_table.turns.index(turn):]
			im_table.dealer = table.dealer
			if table.dice:
				# if current table has dice, we need to image the same dice
				# that also means that the turn is not preflop and players
				# will not be given any dice, thus a manual deal_dice call
				im_table.dice = table.dice
				im_table.deal_dice()
			for i in range(iters):
				# Make player state on the imaginary table equal to the real table
				for i in range(len(table.players)):
					im_table.players[i].active = table.players[i].active
				winners = im_table.play_round()
				if self.seat in winners:
					wins += 1
			chance = wins / iters
			print(("Out of %d random games, I (player %d) have a %.3f chance of winning") % (
				iters, self.seat, chance))
# 			print(im_table.players)
# 			im_table.deal_dice()
# 			print("self dice: ", self.dice)
# 			print("imaginary self dice: ", im_table.players[self.seat].dice)
# 			im_table.rotate_dealer()
# 			input("...")
# 			print("AI self.dice:", self.dice)
			choices = list(self.get_choices(table).keys())
			
			if chance <= 0.3:
				return self.make_fold()
			if 1 in choices:
				choices.remove(0)
			min_choice = 0
			if chance >= 0.5 and (2 in choices or 3 in choices or 4 in choices):
				min_choice = 2
			if chance >= 0.7 and (3 in choices or 4 in choices):
				min_choice = 3
			while True:
				choice = np.random.choice(choices)
				if choice >= min_choice:
					break
			return self.funcs[choice]()
		
	def _human_turn(self, table, turn):
		print("Your turn!")
		active, dice, pot, max_bet = self.table.get_info()
		print("Active players: %d, Dice: %s, Pot: %d, Max bet: %d" % (
			len(active), dice, pot, max_bet))
		print("Your dice: %s, Your stack: %d, your current bet: %d" % (
			str(self.dice), self.stack, self.bet))
		
		choices = self.get_choices(table)
		
		while True:
			for key, choice in choices.items(): 
				print("%d - %s" % (key, choice))
			choice = input("What will you do? ")
			try:
				choice = int(choice)
			except:
				print("Option must be numeric!")
				continue

			if choice in choices:
				return self.funcs[choice]()
			else:
				print("Incorrect option!")
	

def main():
# 	dealer = 0
	player_number = 2
	ai_seats = (1,)							# seat #s start from 0
	table = Table(player_number, ai_seats)

	while True:
		table.play_round()

if __name__ == "__main__":
	main()