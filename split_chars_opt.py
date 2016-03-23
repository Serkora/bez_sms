import graphics
import numpy as np
import money
import time

from graphics import np_to_pil, pil_to_np, Box

def split_characters(image, threshold=255):
	if type(image) == np.ndarray:
		arr = image
		image = np_to_pil(image)
	else:
		arr = pil_to_np(image, mode="L")
	start = 0
	boxes = []
	space = True
	unconnected = 0

	trns = arr.transpose()
# 	whites = trns[np.min(trns) >= threshold]
	whites = np.min(trns) >= threshold
	print(whites)
# 	whites = trns
	
# 	whites[whites >= threshold] = 1
# 	whites[whites <= threshold] = 0
	
# 	print(np.sum(whites))
	
# 	print(arr[arr > 200])
# 
# 	for i, col in enumerate(arr.transpose()):
# 		min_val = np.min(col)
# 	for i in range(arr.shape[1]):
# 		min_val = min(arr[:,i])
# 		if min_val >= threshold and not space:
# 			pass
# 			box = [start, 0, i, arr.shape[0]]
# 			boxes.append(box)
# 			space = True
# 		elif min_val < threshold and space:
# 			start = i
# 			space = False
# 		elif i > 0 and (i - start) > 1 and start != 0 and min_val < threshold:
# 			x, y = arr[:,i], arr[:,i-1]
# 			for j in range(1, arr.shape[0]-1):
# 				if x[j] < threshold and any(np.array([y[j-1], y[j], y[j+1]]) < threshold):
# 					break
# 			else:
# 				box = [start, 0, i, arr.shape[0]]
# 				boxes.append(box)
# 				start = i
					
	if not space:
		box = [start, 0, arr.shape[1], arr.shape[0]]
		boxes.append(box)
		
	return [image.crop(bbox) for bbox in boxes]
	

w = graphics.open_image('images/game/75814.png')
im = money.pot_image(w)
im = im.convert(mode="L")
im = graphics.invert(im)
im = pil_to_np(im, mode="L")
white = np.max(im)
black = np.min(im)
binary_threshold = black + (white - black) * (120 / 255)
im = graphics.binarize(im, binary_threshold)	
# text.show()

def f(im):
# 	chars = None
	for i in range(50):
		chars = split_characters(im)
# 	for char in chars:
# 		char.show()

import cProfile
# cProfile.run('f(im)', sort='tottime')

chars = split_characters(im)
# print(chars)
# for char in chars:
# 	char.show()

# a = np.ones(500).reshape(25,20)
# t = time.time()
# for j in range(50):
# 	for i in range(a.shape[1]):
# 		min(a[:,i])
# print("builtin min: %.3f secs" % (time.time() - t))
# 
# t = time.time()
# for j in range(50):
# 	for i in range(a.shape[1]):
# 		np.min(a[:,i])
# print("np.min: %.3f secs" % (time.time() - t))