import os
import time
import graphics

DEALER_OFFSETS = ((191, 290), (0,0), (325, 105), (611, 162), (578, 289), (452, 326))
DEALER_SIZE = (26,26)

def find_dealer_seat(window):
# 	t = time.time()
	for seat, offset in enumerate(DEALER_OFFSETS):
		box = (offset[0], offset[1], offset[0]+DEALER_SIZE[0], offset[1]+DEALER_SIZE[1])
		img = window.crop(box)
# 		img.show()
# 		input()
# 		red = graphics.colour_ratio(img, "Red")
		green = graphics.colour_ratio(img, "Green")
# 		blue = graphics.colour_ratio(img, "Blue")
		white = graphics.colour_ratio(img, "White", w_thres=500)
# 		print("types: ", type(red), type(green), type(blue), type(white))
# 		print("Red: %.3f, Green: %.3f, Blue: %.3f, White: %.3f" % (red, green, blue, white))
# 		if white > 0.3 and (red / green > 0.8) and (red / blue) > 0.8:
		if white > 0.3 and green < 0.4:
# 		if white > 0.3:
# 			print("Found a dealer in %.3f seconds!" % (time.time() - t))
			return seat
# 		input()