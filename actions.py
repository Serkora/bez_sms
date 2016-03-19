import os
import numpy as np
import graphics
from collections import namedtuple

TOP_OFFSET = 495
FOLD_OFFSET = 385
CC_OFFSET = 520
BR_OFFSET = 660

ACTION_BOX_WIDTH = 120
ACTION_BOX_HEIGHT = 45

FOLD_BOX = (FOLD_OFFSET, TOP_OFFSET, FOLD_OFFSET+ACTION_BOX_WIDTH, TOP_OFFSET+ACTION_BOX_HEIGHT)
CC_BOX = (CC_OFFSET, TOP_OFFSET, CC_OFFSET+ACTION_BOX_WIDTH, TOP_OFFSET+ACTION_BOX_HEIGHT)
BR_BOX = (BR_OFFSET, TOP_OFFSET, BR_OFFSET+ACTION_BOX_WIDTH, TOP_OFFSET+ACTION_BOX_HEIGHT)

TURN_BOX = (CC_OFFSET, TOP_OFFSET, CC_OFFSET+ACTION_BOX_WIDTH//3, TOP_OFFSET+ACTION_BOX_HEIGHT//2)

Action = namedtuple("Action", ['type', 'value'])

def fold():
	cmd = """osascript -e 'tell application "System Events" to keystroke "f" using {shift down}'"""
	os.system(cmd)
	
def check():
	cmd = """osascript -e 'tell application "System Events" to keystroke "c" using {shift down}'"""
	os.system(cmd)
	
def raise_or_bet():
	cmd = """osascript -e 'tell application "System Events" to keystroke "r" using {shift down}'"""
	os.system(cmd)
	
def is_my_turn(window):
	box = window.crop(TURN_BOX)
# 	for col in ["Red", "Green", "Blue", "Black", "White", "Colour"]:
# 		ratio = graphics.colour_ratio(box, col)
# 		print("%s ratio: %.3f" % (col, ratio))
	return graphics.colour_ratio(box, "Red") > 0.5

def fast_fold(window):
	ff = window.crop(FOLD_BOX)
	return graphics.colour_ratio(ff, "Red") > 0.5

def get_actions_tesseract(window):
	if window.mode != "L":
		window = window.convert(mode="L")
	fold_act = None
	cc_act = None
	br_act = None
	
	fold_image = window.crop(FOLD_BOX)
	fold_text = graphics.ocr(fold_image).lower()
# 	print("Fold text: %s" % fold_text)
	if "fold" not in fold_text:
		print("No fold action (text recognized: %s), probably not your turn" % fold_text)
# 		return fold_act, cc_act, br_act
	else:
		fold_act = "Fold"
	
	cc_image = window.crop(CC_BOX)
	cc_text = graphics.ocr(cc_image).lower()
# 	print("CC text: %s" % cc_text)
	if "check" in cc_text:
# 		print("No one has placed any bets, can check")
		cc_act = ("Check", 0)
	elif "call" in cc_text:
		val = "".join(l for l in cc_text if l in "0123456789,.")
		val = val.replace(",", ".")
		val = float(val) if len(val) > 0 else ""
# 		print("Can call for %f dollers" % val)
		cc_act = ("Call", val)
	
	br_image = window.crop(BR_BOX)
	br_text = graphics.ocr(br_image).lower()
# 	print("BR text: %s" % br_text)
	val = "".join(l for l in br_text if l in "0123456789,.")
	val = val.replace(",", ".")
	val = float(val) if len(val) > 0 else ""
	if "bet" in br_text:
# 		print("No one has placed any bets, can bet.")	
		br_act = ("Bet", val)
	elif "raise" in br_text:
# 		print("Someone has placed a bet, can only raise")
		br_act = ("Raise", val)
	
	return fold_act, cc_act, br_act

def get_action_images(window):
	fold = window.crop(FOLD_BOX)
	cc = window.crop(CC_BOX)
	br = window.crop(BR_BOX)
	return fold, cc, br

def call_or_check(window):
	cc = window.crop(BR_BOX)
# 	cc = cc.convert(mode="L")
# 	cc = graphics.invert(cc)
# 	cc.show()
	bbox = graphics.bounding_box(cc, threshold=80, inv=True)
	print((bbox.bottom - bbox.top) / cc.height)
# 	print(bbox)
# 	cc.crop(bbox).show()

def get_cc_images(window):
	cc = window.crop(CC_BOX)
	cc_bbox = graphics.bounding_box(cc, threshold=40, inv=True)
	val_img = cc.crop((0, cc.height//2, cc.width, cc.height))
	if (cc_bbox.bottom - cc_bbox.top) / cc.height > 0.5:
		return cc, val_img
	else:
		return cc, None

def get_br_images(window):
	br = window.crop(BR_BOX)
	val_img = br.crop((0, br.height//2, br.width, br.height))
	type_img = br.crop((0, 0, br.width, br.height//2))
	return br, val_img, type_img

def get_actions(window, *args, **kwargs):
	if not is_my_turn(window):
		return Action("Fold", fast_fold(window)), Action("CC", None), Action("BR", None)
	
	fold_act = Action("Fold", True)
	
	cc_img, val_img = get_cc_images(window)
	if val_img:
		val = graphics.recognize_digits(val_img, 100, *args, **kwargs)
		print("Call val: %s" % val)
		cc_act = Action("Call", val)
	else:
		cc_act = Action("Check", None)
	
	br_img, val_img, type_img = get_br_images(window)
	val = graphics.recognize_digits(val_img, 100, *args, **kwargs)
	if len(graphics.split_characters(type_img)) < 4:
		br_act = Action("Bet", val)
	else:
		br_act = Action("Raise", val)
	
	return fold_act, cc_act, br_act