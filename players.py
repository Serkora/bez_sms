import scipy
import numpy as np
import os
import time
import graphics
from graphics import Offset, Size, Box

PLAYER_BOX_W = 30
PLAYER_BOX_H = 25

CARD_BOX_SIZE = Size(height=25, width=30)
STACK_BOX_SIZE = Size(height=17, width=75)
BET_BOX_SIZE = Size(height=25, width=62)

PLAYER_OFFSETS = ((50, 255), (50, 82), (345, 20), (645, 85), (645, 255))

CARD_OFFSETS_SIX = (Offset(x=50, y=255), Offset(x=50, y=82), Offset(x=345, y=20), 
				Offset(x=645, y=85), Offset(x=645, y=255))
STACK_OFFSETS_SIX = (Offset(x=45, y=310), Offset(x=45, y=138), Offset(x=343, y=72),
				Offset(x=677, y=139), Offset(x=677, y=310))
BET_OFFSETS_SIX = (Offset(x=190, y=270), Offset(x=213, y=143), Offset(x=376, y=110),
				Offset(x=525, y=140), Offset(x=536, y=268))

class Player(object):
	def __init__(self, position, table=6, ocr_threshold=100):
		self.position = position
		self.ocr_threshold = ocr_threshold
		if table == 6:
			o = CARD_OFFSETS_SIX[self.position]
			b = CARD_BOX_SIZE
			self.card_box = Box(o.x, o.y, o.x+b.width, o.y+b.height)
			o = STACK_OFFSETS_SIX[self.position]
			b = STACK_BOX_SIZE
			self.stack_box = Box(o.x, o.y, o.x+b.width, o.y+b.height)
			o = BET_OFFSETS_SIX[self.position]
			b = BET_BOX_SIZE
			self.bet_box = Box(o.x, o.y, o.x+b.width, o.y+b.height)

	def is_in_game(self, window):
		img = window.crop(self.card_box)
		return graphics.colour_ratio(img, "Red") > 0.42
	
	def get_stack(self, window, threshold=None, image=False):
		stack = window.crop(self.stack_box)
		if image: return stack
		
		if not threshold: threshold = self.ocr_threshold
		stack = graphics.recognize_digits(stack, threshold)
		return stack
	
	def get_bet(self, window, threshold=None, image=False):
		bet = window.crop(self.bet_box)
# 		if image: return bet
		
		if not threshold: threshold = self.ocr_threshold
		
		bet_np = graphics.pil_to_np(bet)
		white = graphics.colour_ratio(bet_np, "White")
		if white < 0.01: 
			return None
		else:
				## THIS PART IS BUGGED AS FUCK, but seems to work for now
				## No idea yet how to detect green poker chips to crop the image.
			for i in range(bet_np.shape[1] // 2, bet_np.shape[1]):
				col = bet_np[:,i:i+1]
				max_red_ratio = graphics.max_colour_ratio(col, "Red")
				max_green_ratio = graphics.max_colour_ratio(col, "Red")	# green?!?!
				if max_red_ratio > 0.5:
# 					print("Max red ratio in each pixel in column %d is: %.3f" % (i, max_red_ratio))
					bet = bet.crop((0, 0, i, bet.height))
					break
				if max_green_ratio > 0.334:
# 					print("Max green ratio in column %d is: %.3f" % (i, max_green_ratio))
					bet = bet.crop((0, 0, i-1, bet.height))
					break
			for i in range(bet_np.shape[1] // 2, -1, -1):
				col = bet_np[:,i:i+1]
				max_red_ratio = graphics.max_colour_ratio(col, "Red")
				max_green_ratio = graphics.max_colour_ratio(col, "Red")	# green?!?!
				if max_red_ratio > 0.5:
# 					print("Max red ratio in each pixel in colum %d is : %.3f" % (i, max_red_ratio))
					bet = bet.crop((i+1, 0, bet.width, bet.height))
					break
				if max_green_ratio > 0.334:
# 					print("Max green ratio in column %d is: %.3f" % (i, max_green_ratio))
					bet = bet.crop((i-1, 0, bet.width, bet.height))
					break
# 			bet.show()
			if image: return bet
			bet = graphics.recognize_digits(bet, threshold)
			return bet

def create_players(n=5, table=6):
	players = [Player(i, table) for i in range(n)]
	return players

def get_active_of_players(window, players):
	if window.mode[:3] != "RGB":
		raise TypeError("Cannot do shit with noncolour image! Need RGB(A), given %s" % window.mode)
	
	return [player.is_in_game(window) for player in players]

	
if __name__ == "__main__":
	pass