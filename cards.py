import os
import time
import graphics
import numpy as np

LEFT = 346
# UPPER = 386
UPPER = 342
HEIGHT = 32
WIDTH = 48

OWN_CARDS_BOX = (LEFT, UPPER, LEFT+WIDTH*2, UPPER+HEIGHT)

TABLE_LEFT_OFFSET = 263
TABLE_TOP_OFFSET = 183
TABLE_GAP = 54

CARDS = {}
SUITS = {'s': "spades", 'c': "clubs", 'h': "hearts", 'd': "diamonds"}
NAMES = {'J': "Jack", 'Q': "Queen", 'K': "King", 'A': "Ace"}

for im in [f for f in os.listdir("images/cards") if "png" in f]:
	card_name = im[:-4]	
	CARDS[card_name] = graphics.open_image("images/cards/%s" % im, grey=True, array=True)

# for card, img in CARDS.items(): print(img)

class Card(object):
	Suits = {'s': "spades", 'c': "clubs", 'h': "hearts", 'd': "diamonds"}
	Values = {'J': "Jack", 'Q': "Queen", 'K': "King", 'A': "Ace"}

	def __init__(self, value=None, suit=None, key=None):
		if key:
			self.value = key[:-1]
			self.suit = key[-1]
		else:
			self.value = value
			self.suit = suit
		if self.value in "JQKA":
			self._value = 11 + "JQKA".index(self.value)
		elif self.value:
			self._value = int(self.value)

	def __repr__(self):
		if not self.value:
			return "Unrecognized card"
		if self.value and self._value > 10:
			val = self.Values[self.value]
		else:
			val = self.value
		suit = self.Suits[self.suit]
		return "%s of %s" % (val, suit)


def own_cards_image(window, bw=True):
	img = window.crop(OWN_CARDS_BOX)
	if bw and img.mode != "L":
		img = img.convert(mode="L")

	return img
	
def find_card(img, exact=False):
	match, mse = False, float("+inf")
	for card, db_image in CARDS.items():
		if exact:
			if graphics.images_match(img, db_image): 
				return card, 0
		else:
			temp_mse = graphics.image_difference(img, db_image)
			if temp_mse < mse:
				mse = temp_mse
				match = card
	return match, mse

def own_cards(image=None, text=False, exact=False):
	if not image:
		image = own_cards_image()
	cards = []
	for i in range(2):
		card = image.crop((WIDTH*i, 0, WIDTH*(i+1), HEIGHT))
		card = np.array(card, np.uint8)
		card, mse = find_card(card, exact=exact)
		if mse > 25: card = None
		cards.append(card)
	# if text:
		# cards = [card_name(card) for card in cards]
	cards = [Card(key=card) for card in cards]

	return cards

def table_card(window, n=0, exact=False, text=False):
	box = (TABLE_LEFT_OFFSET + TABLE_GAP * n, TABLE_TOP_OFFSET, 
		TABLE_LEFT_OFFSET + TABLE_GAP * n + WIDTH, TABLE_TOP_OFFSET + HEIGHT)
	card = window.crop(box)
	if card.mode != "L":
		card = card.convert(mode="L")
# 	card.show()
	card = np.array(card, np.uint8)
	match, mse = find_card(card, exact=exact)
	if mse > 25: match = None
	# print("mse: ", mse)
	# if text:
	# 	match = card_name(match)
	if match:
		return Card(key=match)
	else:
		return None

if __name__ == "__main__":
	pass
# 	while True:
# 		get_card_image()
# 		t = time.time()
# 		for i in range(20):
# 			img = pys.grab(bbox=LEFT_CARD).convert("L")
# 		print("20 x screenshot+convert took %f seconds" % (time.time() - t))
# 		for i in range(20):
# 			get_own_cards(text=True)
# 		print("20 x get_own_cards: %f s" % (time.time() - t))
# 		print("Your cards are: %s and %s" % get_own_cards(text=True))
# 		lc = get_card_image(image=True)
# 		lc.show()
# 		match, mse = match_card(lc, exact=True)
# 		print("Your left card is: %s, mse: %f" % (match, mse), end="\n")
# 		input()
#     imgs = [f for f in os.listdir("images/cards") if "png" in f]
#     print(imgs)