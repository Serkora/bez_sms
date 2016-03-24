import numpy as np
import itertools

COMBINATIONS = ["High", "Pair", "Two pairs", "Three of a kind", "Small straight",
				"Big straight", "Even", "Odd", "Full house", "Four of a kind", "Poker"]

class Table(object):
	def __init__(self, players, ai_seats, small_blind=2):
		self.players = self.generate_players(players, ai_seats)
		self.small_blind = small_blind
		self.round_pot = 0
		self.turn_pot = 0
		self.max_bet = 0
		self.dice = None
	
	def generate_players(self, players, ai_seats):
		plrs = []
		for seat in range(players):
			plrs.append(Player(self, seat, seat in ai_seats))
		return plrs
	
	def update(self):
		self.max_bet = max(p.bet for p in self.players)
		self.turn_pot = sum(p.bet for p in self.players)
		if self.get_info()[0] == 1:
			return True
	
	def get_info(self):
# 		return ("Active players: %d, Dice: %s, Pot: %d, Max bet: %d" % (
# 			len(self.players), str(self.dice), self.pot, self.max_bet))
		active = [p for p in self.players if p.active]
		return active, str(self.dice), self.round_pot + self.turn_pot, self.max_bet
	
	def next_dealer(self):
		self.players.append(self.players.pop())			# second player becomes first etc
	
	def start_turn(self, turn):
		if turn == "preflop":
			self.round_pot = 0
			self.turn_pot = 0
			self.max_bet = None
			for p in self.players: 
				p.bet = 0 
				p.active = True
			self.deal_dice()
			self.blinds()
		elif turn == "flop":
			self.dice = tuple(np.random.choice(range(1,7),5))	
	
	def end_turn(self, turn):
		active = self.get_info()[0]
		if len(active) == 1:
			print("Player %d has won %d coins!" % (active[0].seat, self.pot))
			self.active[0].stack += self.pot
		else:
			for player in self.players:
				self.max_bet = 0
				player.bet = 0
			self.round_pot += self.turn_pot
			self.turn_pot = 0
		if turn == "flop":
			pass
	
	def deal_dice(self):
		for player in self.players:
			player.dice = tuple(np.random.choice(range(1,7),2))	
	
	def blinds(self):
		self.players[0].make_bet(self.small_blind)
		self.players[1].make_bet(self.small_blind * 2)
	

class Player(object):
	def __init__(self, table, seat, ai=False, stack=50):
		self.table = table
		self.seat = seat
		self.ai = ai
		self.dice = (0,0)
		self.stack = stack
		self.bet = 0
		self.active = True
	
	def __repr__(self):
		text = "AI " if self.ai else "Human "
		text += "player at seat %d. " % self.seat
		text += "Dice: %d, %d" % (self.dice)
		return text

	def make_fold(self):
		self.active = False

	def make_check(self):
		pass

	def make_call(self):
		self.make_bet(self.table.max_bet)

	def make_bet(self, value=None):
		if value is None:
			value = self.table.small_blind * 2
		print("bet: ", self.bet, "value: ", value, "stack: ", self.stack)
		self.stack -= (value - self.bet)
		self.bet = value
		print("bet: ", self.bet, "value: ", value, "stack: ", self.stack)

	def make_raise(self, value=None):
		if value is None:
			value = self.table.small_blind * 4
		self.make_bet(value)

	def calculate_hand_score(self, dice):
		if len(dice) < 3:
			raise ValueError("Can't calculate hand score with less than 5 dice!")
		elif self.dice == (0,0):
			raise ValueError("Can't caluclate hand score without own dice!")
		print("Your dice: %d, %d; Table dice: %s" % (self.dice + (", ".join(map(str, dice)),)))
		flop_combinations = itertools.permutations(dice, 3)
		best_hand = (0, ())
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
			return 10				# definitely a poker
		elif len(dice_set) == 2:	# (a,a,b,b,b), (a,a,a,b,b), (a,b,b,b,b), (a,a,a,a,b)
			# four of a kind or full house
			if len(set(dice_sorted[1::2])) == 1:
				return 9			# if elements 1 and 3 are equal, the four of a kind
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
	
	def turn(self, table, turn):
		# turn is "preflop" or "flop"
		if not self.active:
			return

		if self.ai:
			self._ai_turn(table, turn)
		else:
			self._human_turn(table, turn)
	
	def _ai_turn(self, table, turn):
		pass
		
	def _human_turn(self, table, turn):
		print("Player %d turn!" % self.seat)
		active, dice, pot, max_bet = self.table.get_info()
		print("Active players: %d, Dice: %s, Pot: %d, Max bet: %d" % (
			len(active), dice, pot, max_bet))
		print("Your dice: %s, Your stack: %d, your current bet: %d" % (
			str(self.dice), self.stack, self.bet))
		choices = {0: "Fold", 1: "Check", 2: "Call", 3: "Bet bb", 4: "bet 2 bb"}
		funcs = [self.make_fold, self.make_check, self.make_call, self.make_bet, self.make_raise]
		while True:
			choice = input("What will you do? ")
			try:
				choice = int(choice)
			except:
				print("Option must be numeric!")
				continue

			if choice in choices:
				funcs[choice]()
				break
			else:
				print("Incorrect option!")
	

def main():
# 	dealer = 0
	player_number = 2
	ai_seats = (5,)							# seat #s start from 0
	table = Table(player_number, ai_seats)
# 	print(table.players)
	
# 	p = table.players[0]
# 	prev_score = -1
# 	prev_comb = (1,2,3,4,5)
# 	c = (2,5,3,4,6)
# 	score = p.calculate_combination_score(c)
# 	print("%s — %s" % (", ".join(map(str, c)), COMBINATIONS[score]))	
# 	return
# 	for i in range(20):
# 		c = np.random.choice((1,2,3,4,5,6), 5)
# 		score = p.calculate_combination_score(c)
# 		print("%s — %s" % (", ".join(map(str, c)), COMBINATIONS[score]))
# 		if score == prev_score:
# 			cmp = p.compare_same_combination(score, c, prev_comb)
# 			if cmp == 1:
# 				print(c, " is higher, than ", prev_comb)
# 			elif cmp == 0:
# 				print(c, " is the same as ", prev_comb)
# 			elif cmp == -1:
# 				print(c, " is weaker, than ", prev_comb)
# 		prev_score = score
# 		prev_comb = c
# 	
# 	return
# 	for i in range(20):
# 		p.dice = tuple(np.random.choice((1,2,3,4,5,6), 2))
# 		flop = np.random.choice((1,2,3,4,5,6), 5)
# 		best_hand = p.calculate_hand_score(flop)
# 		print(p.dice, flop, best_hand)
# 	return
	while True:
		print("------------------\nNew Round!")
		table.next_dealer()
		for turn in ["preflop", "flop"]:
			table.start_turn(turn)
			for player in table.players:
				if table.update():
					break
				player.turn(table, turn)
				if table.update():
					break
			if table.end_turn(turn):
				break
		
# 		dealer += 1
# 		dealer %= players

if __name__ == "__main__":
	main()