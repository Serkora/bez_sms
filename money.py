import os
import time
import graphics
import PIL
import PIL.ImageOps
import numpy as np
from graphics import Offset, Size, Box

POT_BOX = (355,268,420,285)
MONEY_BOX = Size(height=17, width=75)

own_stack_OFFSET = Offset(x=380, y=405)
own_stack_BOX = (own_stack_OFFSET.x, own_stack_OFFSET.y, own_stack_OFFSET.x + MONEY_BOX.width,
			own_stack_OFFSET.y + MONEY_BOX.height)


def pot_image(window):
	img = window.crop(POT_BOX)
	
	return img

def own_stack_image(window):
	img = window.crop(own_stack_BOX)
	
	return img

def pot(window):
	pot_img = pot_image(window)
# 	pot_img.show()
	
	white = graphics.colour_ratio(pot_img, "White", w_thres=500)
	
	if white < 0.01:
		return

	pot = graphics.recognize_digits(pot_img)

	return pot
	
def own_stack(window):
	stack_img = own_stack_image(window)
# 	stack_img.show()
	
	stack = graphics.recognize_digits(stack_img)
	return stack

	return img