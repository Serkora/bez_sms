import os
import time
import sys
import pickle

import graphics
import actions
import cards
import players
import dealer
import money
import recognition

import PIL
import PIL.ImageDraw

from threading import Thread
from multiprocessing import Process

from logger import Logger
logger = Logger(__name__, Logger.DEBUG)

GAME_WINDOW_RGB = None
GAME_WINDOW_GREY = None
GAME_WINDOW_TIME = 0
REFRESH_RATE = -1		# limits the screent shot rate. Makes it safe to call game_window
						# function in any function that needs the whole window without
						# the severe performance reduction.
						# Although, all of the functions take 'window' as an argument.

# GAME_WINDOW_BOX = ('left','upper','right','bottom')
GAME_WINDOW_OFFSET = (0,43)
GAME_WINDOW_SIZE = (545, 790)

GAME_WINDOW_BOX = (GAME_WINDOW_OFFSET[0], GAME_WINDOW_OFFSET[1], 
			GAME_WINDOW_OFFSET[0]+GAME_WINDOW_SIZE[1], GAME_WINDOW_OFFSET[1]+GAME_WINDOW_SIZE[0])

def set_window_pos(x=0,y=0):
	cmd="""osascript -e 'tell application "System Events"
		set position of first window of application process "PokerStars.net" to {%d, %d}
	end tell'""" % (x,y)
	# print(cmd)
	os.system(cmd)

set_window_pos()
	
def game_window(grey=False, path=None, force=False):
	global GAME_WINDOW_RGB, GAME_WINDOW_GREY, GAME_WINDOW_TIME
	if (time.time() - GAME_WINDOW_TIME) > REFRESH_RATE or force:
		GAME_WINDOW_TIME = time.time()
		try:
			GAME_WINDOW_RGB = graphics.grab(bbox=GAME_WINDOW_BOX)	
		except OSError:				# на OSX 10.6 приходится целиком экран снимать и потом обрезать. Впрочем, тут и покерстарс не запускаются, лол.
			GAME_WINDOW_RGB = graphics.grab().crop(GAME_WINDOW_BOX)
		# if not path:
		# 	GAME_WINDOW_RGB = graphics.open_image("images/game/game_window_act.png")
		# else:
		# 	GAME_WINDOW_RGB = graphics.open_image(path)
		
		GAME_WINDOW_GREY = GAME_WINDOW_RGB.convert("L")
	if grey:
		return GAME_WINDOW_GREY
	else:
		return GAME_WINDOW_RGB

def build_recognition_db(binary_threshold, window=None, strings=None, show=False, neural=False, *args, **kwargs):
	if not window:
		window = game_window()
	elif type(window) == str:
		window = graphics.open_image(window)
# 	window.show()
	
	if not strings:
		strings = input("Enter the strings in the game window in the following order: "
						"pot, your stack, starting from the player to your left, clockwise, "
						"player 1 stack, player 1 bet, player 2 stack, etc, then call value "
						"and bet/raise value, separated by spaces. If no bet, call or raise, "
						"just press spacebar again.\nAlternatively, you can input the "
						"filename where all that info is stored.\nOr just press enter and "
						"input each image text separately when prompted.\n").split(" ")
	elif type(strings) == str:
		strings = strings.split(" ")

	if len(strings) == 1:
		if strings[0] == "":
			show = True
		else:
			with open(strings[0], 'r') as f:
				strings = f.read().strip("\n").split(" ")
	def gen():
		if strings:
			yield strings.pop(0)
		else:
			yield None
	def next_string():
		return strings.pop(0) if strings else None
# 		return gen().__next__()

	print(strings)
	
	pot_digits, pot_img = next_string(), money.pot_image(window)
	if graphics.colour_ratio(pot_img, "White", w_thres=500) > 0.01:
		graphics.update_recognition_db(pot_img, binary_threshold, show=show, ics=pot_digits, neural=neural)
	graphics.update_recognition_db(money.own_stack_image(window), binary_threshold, show=show, ics=next_string(), neural=neural)
	plrs = players.create_players()
	for player in plrs:
		graphics.update_recognition_db(player.get_stack(window, image=True), binary_threshold, show=show, ics=next_string(), neural=neural)
		bet_image = player.get_bet(window, image=True)
		bet = next_string()
		if bet_image:
			graphics.update_recognition_db(bet_image, binary_threshold, show=show, ics=bet, neural=neural)
	if actions.is_my_turn(window):
		_, call = actions.get_cc_images(window)
		call_digits = next_string()
		if call:
			graphics.update_recognition_db(call, binary_threshold, show=show, ics=call_digits, neural=neural)
		_, br, _ = actions.get_br_images(window)
		graphics.update_recognition_db(br, binary_threshold, show=show, ics=next_string(), neural=neural)

def all_info(path=None):
	window = game_window(path=path)
	window.show()
	pot = money.pot(window)
	own_stack = money.own_stack(window)
	own_cards_image = cards.own_cards_image(window)
	own_cards = cards.own_cards(own_cards_image)
	flop = [cards.table_card(window, i) for i in range(3)]
	turn = cards.table_card(window, 3)
	river = cards.table_card(window, 4)
	
	plrs = players.create_players()
	info = []
	for i, p in enumerate(plrs):
		text = "Player %d: \n" % i
		text += "\tStack: %s\n" % str(p.get_stack(window))
		text += "\tBet: %s" % str(p.get_bet(window))
		info.append(text)
	
	
	print("\n")
	print("pot: ", pot)
	print("my stack: ", own_stack)
	print("own cards: ", own_cards)
	print("flop: ", flop)
	print("turn: ", turn)
	print("river: ", river)
	for text in info:
		print(text)

	text = "Actions:\n"
	for action in actions.get_actions(window):
		text += "\t%s: %s\n" % (action.type, str(action.value))
	print(text)

def _create_image_with_info(window):
	threshold = 100
	font_size = 17
	pot = money.pot_image(window)
	if graphics.colour_ratio(pot, "White") >= 0.01:
		pot = recognition.recognize_digits(pot, threshold)
	else:
		pot = "NO POT!"
	draw = PIL.ImageDraw.Draw(window)
	font = PIL.ImageFont.truetype("data/font.ttf", font_size)
	draw.text((330, 270),"POT SIZE: %s" % pot,(255,0,0), font=font)
	del draw
	
	own_stack = money.own_stack_image(window)
	own_stack = recognition.recognize_digits(own_stack, threshold)
	draw = PIL.ImageDraw.Draw(window)
	font = PIL.ImageFont.truetype("data/font.ttf", font_size)
	draw.text((330, 435),"MY STACK: %s" % own_stack,(255,0,0), font=font)
	del draw
	
	seat = dealer.find_dealer_seat(window)
	loc = dealer.DEALER_OFFSETS[seat]
	loc = (loc[0]-60, loc[1] + 20)
	draw = PIL.ImageDraw.Draw(window)
	font = PIL.ImageFont.truetype("data/font.ttf", font_size)
	draw.text(loc,"DEALER HERE (player %d)!" % (seat + 1),(255,0,0), font=font)
	del draw	

	for j in range(5):
		p = players.Player(j)
		if p.is_in_game(window):
			text = "PLAYER IS ACTIVE"
		else:
			text = "PLAYER INACTIVE"
		draw = PIL.ImageDraw.Draw(window)
		font = PIL.ImageFont.truetype("data/font.ttf", font_size)
		loc = (p.card_box.left-20, p.card_box.top-20)
		draw.text(loc, text, (255, 0, 0), font=font)
		del draw
		
		stack = window.crop(p.stack_box)
		stack = recognition.recognize_digits(stack, threshold)
		draw = PIL.ImageDraw.Draw(window)
		font = PIL.ImageFont.truetype("data/font.ttf", font_size)
		loc = (p.stack_box.left-20, p.stack_box.top+20)
		draw.text(loc, "STACK: %s" % stack, (255, 0, 0), font=font)
		del draw
		
		bet = window.crop(p.bet_box)
		bet_np = graphics.pil_to_np(bet)
		white = graphics.colour_ratio(bet_np, "White")
		if white < 0.01: 
			text = "NO BETS HERE!"
		else:
			for i in range(bet_np.shape[1] // 2, bet_np.shape[1]):
				col = bet_np[:,i:i+1]
				max_red_ratio = graphics.max_colour_ratio(col, "Red")
				max_green_ratio = graphics.max_colour_ratio(col, "Red")
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
				if max_red_ratio > 0.5:
# 					print("Max red ratio in each pixel in colum %d is : %.3f" % (i, max_red_ratio))
					bet = bet.crop((i+1, 0, bet.width, bet.height))
					break
			text = "PLACED A BET: %s" % recognition.recognize_digits(bet, threshold)

		draw = PIL.ImageDraw.Draw(window)
		font = PIL.ImageFont.truetype("data/font.ttf", font_size)
		loc = (p.bet_box.left-40, p.bet_box.top-20 + (int(j == 2) * 40))
		draw.text(loc, text, (255, 0, 0), font=font)
	
	cc, val_img = actions.get_cc_images(window)
	call = recognition.recognize_digits(val_img)
	draw = PIL.ImageDraw.Draw(window)
	font = PIL.ImageFont.truetype("data/font.ttf", font_size*1.5)
	loc = (540, 490)
	draw.text(loc, call, (0, 255, 0), font=font)
	
	br, val_img, _ = actions.get_br_images(window)
	bet = recognition.recognize_digits(val_img)
	draw = PIL.ImageDraw.Draw(window)
	font = PIL.ImageFont.truetype("data/font.ttf", font_size*1.5)
	loc = (660, 490)
	draw.text(loc, bet, (0, 255, 0), font=font)

	
# 	my_card = cards.
	
# 	window.show()
	return window

def create_image_with_info():
	window = game_window()
	# window = game_window(path="images/game/s7.png")
	# window.show()
	try:
		window = _create_image_with_info(window)
	except:
		pass
	return window

# all_info(path="images/game/s2.png")
# create_image_with_info()
# for i in range(20):
# 	build_recognition_db(90+i, "images/game/s4.png", strings="s4.txt", show=False)
# build_recognition_db(110, "images/game/s7.png", strings="s7.txt", show=False, neural=True)
# build_recognition_db(110, "images/game/s4.png", strings="s4.txt", show=False, neural=True)
# build_recognition_db(110, "images/game/s3.png", strings="s3.txt", show=False, neural=True)
# build_recognition_db(110, "images/game/s2.png", strings="s2.txt", show=False, neural=True)

# recognition.train(100)

# with open(recognition.NET_PATH, 'wb') as f:
# 	pickle.dump(recognition.NETWORK, f)
	
# for img in ["s7.png", "8120.png", "75814.png"]:
# 	w = game_window(path="images/game/%s" % img)
# 	p = money.pot_image(w)
# 	logger.info("Digits recognized: %s" % recognition.recognize_digits(p))
# 
# w = game_window(path="images/game/s2.png")
# s = money.own_stack_image(w)
# t = time.time()
# logger.info("Digits recognized: %s" % recognition.recognize_digits(s))

# create_image_with_info()