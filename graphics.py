import os
import os.path
import time
import sys
from collections import namedtuple, defaultdict

import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
import pyscreenshot as pys
# import pytesseract as pyt
import numpy as np

import recognition
from logger import Logger
logger = Logger(__name__, Logger.INFO)

Offset = namedtuple("Offset", ['x','y'])
Size = namedtuple("Size", ['height', 'width'])
Box = namedtuple("Box", ['left', 'top', 'right', 'bottom'])

	### Image information ### 

def colour_ratio(image, col, *args, **kwargs):
	if type(image) != np.ndarray:
		image = pil_to_np(image)
# 	if "pixel" in kwargs and kwargs['pixel'] == True:
# 		return _colour_ratio_pixel(image, col, *args, **kwargs)
	if type(col) == str and col in ["Black", "White", "Colour", "Grey"]:
		return _colour_ratio_bw(image, col, *args, **kwargs)
	elif type(col) == int or (type(col) == str and col in ["Red", "Green", "Blue"]):
		return _colour_ratio_rgb(image, col, *args, **kwargs)

def _colour_ratio_bw(array, col, colour=False, *args, **kwargs):
	if len(array.shape) < 3 and not colour:
		return _colour_ratio_bw_from_greyscale(array, col, *args, **kwargs)
	else:
		return _colour_ratio_bw_from_rgb(array, col, *args, **kwargs)

def _colour_ratio_rgb(array, col, offset=(0,0), size=None, w_thres=None,
		*args, **kwargs):
	if len(array.shape) == 2:
		array.reshape(1, array.shape[0], array.shape[1])
	if type(col) == str:
		col = ["Red", "Green", "Blue"].index(col)
	total = 0
	colour = 0
	if size:
		height = min(size[0], array.shape[0] - offset[0])
		width = min(size[1], array.shape[1] - offset[1])
	else:
		height = array.shape[0] - offset[0]
		width = array.shape[1] - offset[1]

	slice = array[offset[0]:offset[0]+height,offset[1]:offset[1]+width,:3]

	if w_thres:
		slice = slice[np.sum(slice, axis=2) <= w_thres]
		colour = np.sum(slice[:,col])
	else:
		colour = np.sum(slice[:,:,col])
	total = np.sum(slice)
	
# 	print("Total: %d, colour: %d" % (total, colour))	
	return colour / max(total, 0.00001)
		
def _colour_ratio_bw_from_greyscale(array, col, offset=(0,0), size=None, 
		b_thres=50, w_thres=200, *args, **kwargs):
	if len(array.shape) < 2:
		array = array.reshape(1, array.shape[0])
	o = offset
	if size:
		height = size[0]
		width = size[1]
	else:
		height = array.shape[0]
		width = array.shape[1]
	total = height * width

	black = np.sum(array[o[0]:o[0]+height][o[1]:o[1]+width] < b_thres)
	white = np.sum(array[o[0]:o[0]+height][o[1]:o[1]+width] > w_thres)
	grey = total - black - white
	
	if col == "Black":
		return black / total
	elif col == "White":
		return white / total
	elif col == "Grey":
		return grey / total	

def _colour_ratio_bw_from_rgb(array, col, offset=(0,0), size=None, 
		b_thres=50, w_thres=500, *args, **kwargs):
	if len(array.shape) == 2:
		array.reshape(1, array.shape[0], array.shape[1])
	o = offset
	if size:
		height = size[0]
		width = size[1]
	else:
		height = array.shape[0]
		width = array.shape[1]
	total = height * width
	
	black = np.sum(np.sum(array[o[0]:o[0]+height, o[1]:o[1]+width, :3], axis=2) < b_thres)
	white = np.sum(np.sum(array[o[0]:o[0]+height, o[1]:o[1]+width, :3], axis=2) > w_thres)
	colour = total - black - white

	if col == "Black":
		return black / total
	elif col == "White":
		return white / total
	elif col == "Colour":
		return colour / total

# def _colour_ratio_pixel(pixel, col, *args, **kwargs):
# 	if type(col) == str:
# 		idx = ["Red", "Green", "Blue"].index(col)
# 	else:
# 		idx = col
# 		
# 	total = np.sum(pixel[:,:,:3])

def max_colour_ratio(image, col, colour=False, *args, **kwargs):
	array = pil_to_np(image)
	if type(col) == str and col in ["Black", "White"]:
		if colour:
			_max_colour_ratio_bw_from_rgb(image, col, *args, **kwargs)
		else:
			_max_colour_ratio_bw_from_greyscale(image, col, *args, **kwargs)
	elif type(col) == str and col in ["Red", "Green", "Blue"]:
		return _max_colour_ratio_rgb(array, col, *args, **kwargs)
	
def _max_colour_ratio_rgb(array, col, threshold=0, *args, **kwargs):
	if type(col) == str:
		col = ["Red", "Green", "Blue"].index(col)

	array = array[array[:,:,col] > threshold]
	if len(array) == 0: return 0

	total = np.sum(array[:,:3],1)
	total[total == 0] = 1 				# if total is zero, so is colour, but no division by zero this way
	colour = array[:,col]
	
	return np.max(colour / total)

def colour_sections(image, col, *args, **kwargs):
	arr = pil_to_np(image)
	if type(col) == str and col in ["Black", "White", "Grey", "Colour"]:
		return _colour_sections_bw(image, col, *args, **kwargs)
	elif type(col) == str and col in ["Red", "Green", "Blue"]:
		return _colour_sections_rgb(image, col, *args, **kwargs)

def _colour_sections_bw(array, col, b_thres=50, w_thres=200):
	if len(array.shape) > 1:
		array = array[:, array.shape[1] // 2]
	
	w_counter, w_flag = 0, False
	b_counter, b_flag = 0, False
	g_counter, g_flag = 0, False
	
	for pixel in array:
		if pixel < b_thres:
			w_flag, g_flag = False, False
			if not b_flag: 
				b_counter += 1
				b_flag = True
		elif pixel > w_thres:
			b_flag, g_flag = False, False
			if not w_flag:
				w_counter += 1
				w_flag = True
		else:
			if not g_flag:
				g_counter += 1
				g_flag = True
	
	if col == "Black": return b_counter
	elif col == "White": return w_counter
	elif col == "Grey": return g_counter

def bounding_box(image, threshold=None, inv=False):
	if not threshold: threshold = 40
	if type(image) != np.ndarray:
		if image.mode != "L":
			image = image.convert(mode="L")
		if inv:
			image = invert(image)
		arr = np.array(image, np.uint8)
	else:
		arr = image
	
	box = [0, 0, arr.shape[1], arr.shape[0]]
# 	box = Box(left=0, top=0, right=arr.shape[1], bottom=arr.shape[0])
	for i in range(arr.shape[0]):			# top
		if min(arr[i]) < threshold:
			box[1] = i
			break
	for i in range(arr.shape[0]-1,-1,-1):	# bottom
		if min(arr[i]) < threshold:
			box[3] = min(i+1, arr.shape[0])
			break
	for i in range(arr.shape[1]):			# left
		if min(arr[:,i]) < threshold:
			box[0] = i
			break
	for i in range(arr.shape[1]-1,-1,-1):	# right
		if min(arr[:,i]) < threshold:
			box[2] = min(i+1, arr.shape[1])
			break
	box = Box(*box)

	return box

def top_bottom_ratio(image, threshold=0):
	arr = pil_to_np(image, mode="L")
	width = arr.shape[0]
	middle = width // 2
	odd = int(width % 2 != 0)
		
	top = arr[0:middle+odd]
	bottom = arr[middle:]
	
	return np.sum(top <= threshold) / np.sum(bottom <= threshold)

def left_right_ratio(image, threshold=0):
	arr = pil_to_np(image, mode="L")
	width = arr.shape[1]
	middle = width // 2
	odd = int(width % 2 != 0)
		
	left = arr[:,0:middle+odd]
	right = arr[:,middle:]

	return np.sum(left <= threshold) / np.sum(right <= threshold)	

def centroid(image):
	arr = pil_to_np(image, mode="L")
	total = np.sum(arr)
	if total == 0:
		return Centroid(0,0,0)

	x_sum = 0
	y_sum = 0
	for i in range(arr.shape[0]):
		y_sum += np.sum(arr[i]) * i
	for i in range(arr.shape[1]):
		x_sum += np.sum(arr[:,i]) * i
	loc = (x_sum // total, y_sum // total)
	centroid = Centroid(*loc, ratio=loc[1]/loc[0])
	return centroid

	### Operations on images ###

def binarize(image, threshold=127):
	arr = pil_to_np(image, "L")
		
	arr[arr >= threshold] = 255
	arr[arr < threshold] = 0
	
	return arr
	
def ternarize(image, b_thres=80, w_thres=160):
	arr = pil_to_np(image, "L")
		
	for i in range(arr.shape[0]):
		for j in range(arr.shape[1]):
			v = arr[i][j]
			arr[i][j] = 127 * (int(v > b_thres) + int(v > w_thres)) + 1 * int(v > b_thres)
	return arr

def image_filter(image, ftype, *args, **kwargs):
	arr = pil_to_np(image)
	if ftype == "low": 
		return low_pass(image, *args, **kwargs)
	elif ftype == "high":
		return high_pass(image, *args, **kwargs)
	elif ftype == "band":
		return band_pass(image, *args, **kwargs)

def low_pass(image, threshold, pil=False):
	arr = pil_to_np(image)
	arr[arr > threshold] = 255
	
	if pil:
		return np_to_pil(arr)
	else:
		return arr

def high_pass(image, threshold, pil=False):
	arr = pil_to_np(image)
	arr[arr < threshold] = 0
	
	if pil:
		return np_to_pil(arr)
	else:
		return arr
	
def band_pass(image, b_thres, w_thres, pil=False):
	if b_thres > w_thres:
		raise ValueError("White threshold cannot be lower than black!")
	arr = pil_to_np(image)
	arr = low_pass(arr, w_thres)
	arr = high_pass(arr, b_thres)
	
	if pil:
		return np_to_pil(arr)
	else:
		return arr

def merge_pixel_colours(pixel_bg, pixel_fg):
	bg_a = pixel_bg[3] / 255
	fg_a = pixel_fg[3] / 255
	a = (fg_a + bg_a * (1 - fg_a)) * 255
	r = pixel_fg[0] * fg_a + pixel_bg[0] * bg_a * (1 - fg_a)
	g = pixel_fg[1] * fg_a + pixel_bg[1] * bg_a * (1 - fg_a)
	b = pixel_fg[2] * fg_a + pixel_bg[2] * bg_a * (1 - fg_a)
	
	return np.array([r,g,b,a])

def overlay_rgba_images(img_bg, img_fg, loc, merge=True):
	bg = np.array(img_bg, np.uint8)
	fg = np.array(img_fg, np.uint8)
	for i in range(img_fg.height):
		for j in range(img_fg.width):
			if merge:
				bg[i+loc[0]][j+loc[1]] = merge_pixel_colours(bg[i+loc[0]][j+loc[1]], fg[i][j])
			else:
				bg[i+loc[0]][j+loc[1]] = fg[i][j]

	return np_to_pil(bg, img_bg.size)
	
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
	
	for i in range(arr.shape[1]):
		min_val = min(arr[:,i])
		if min_val >= threshold and not space:
			box = [start, 0, i, arr.shape[0]]
			boxes.append(box)
			space = True
		elif min_val < threshold and space:
			start = i
			space = False
		elif i > 0 and (i - start) > 1 and start != 0 and min_val < threshold:
			x, y = arr[:,i], arr[:,i-1]
			for j in range(1, arr.shape[0]-1):
				if x[j] < threshold and any(np.array([y[j-1], y[j], y[j+1]]) < threshold):
					break
			else:
				box = [start, 0, i, arr.shape[0]]
				boxes.append(box)
				start = i
					

	if not space:
		box = [start, 0, arr.shape[1], arr.shape[0]]
		boxes.append(box)
		
	return [image.crop(bbox) for bbox in boxes]
	
def crop_to_bounding_box(image, threshold=None):
	box = bounding_box(image, threshold)
	return image.crop(box)

	### Image conversion ###

def np_to_pil(arr, size=None, mode=None):
	if type(arr) != np.ndarray:
		return arr

	if len(arr.shape) < 2:
		arr = arr.reshape(1, arr.shape[0])
	elif len(arr.shape) < 3 and mode and mode in "RGBA":
		arr = arr.reshape(1, arr.shape[0], arr.shape[1])

	if not size:
		size = arr.shape[1::-1]
	if not mode:
		if len(arr.shape) in [1,2]:
			mode = "L"
		elif arr.shape[2] == 3:
			mode = "RGB"
		elif arr.shape[2] == 4:
			mode = "RGBA"
	if not mode:
		raise ValueError("Image mode couldn't have been inferred from array shape.")
		
	if mode in "RGBA":								# covers both RGB and RGBA
		arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2])
		if len(arr[0]) == 3 and mode == "RGBA":		# RGB -> RGBA
			arr = np.c_[arr, 255*np.ones((len(arr),1), np.uint8)]
	elif mode == "L":
		arr = arr.reshape(arr.shape[0] * arr.shape[1])

	try:		
		img = PIL.Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)
	except Exception as e:
		logger.error("Couldn't convert numpy array to PIL image!"
			"Returning one black pixel. Error: %s" % str(e))
		arr = np.array([[0]*len(mode)])
		img = PIL.Image.frombuffer(mode, (1,1), arr.tostring(),'raw', mode, 0, 1)

	return img

def pil_to_np(image, mode=None, bits=np.uint8):
	if type(image) != np.ndarray:
		if mode and image.mode != mode:
			image = image.convert(mode=mode)
		try:
			arr = np.array(image, bits)
		except Exception as e:
			logger.error("Couldn't convert PIL image to numpy array!"
				"Returning one empty array. Error: %s" % str(e))		
			arr = np.array([[]], bits)
	else:
		arr = image

	return arr

	### Image comparison / recognition ###

def image_difference(img_a, img_b, rms=False):
	square_error = np.sum((img_a - img_b) ** 2)
	mean_square_error = square_error / (img_a.shape[0] * img_a.shape[1])
	if rms:
		return mean_square_error ** 0.5
	else:
		return mean_square_error

def images_match(img_a, img_b):
	if img_a.shape != img_b.shape:
		return False
	for i in range(img_a.shape[0]):
		for j in range(img_a.shape[1]):
			if img_a[i][j] != img_b[i][j]: 
				return False
	return True

def image_characters(image, binary_threshold, normalize=True, inv=True, show=False):
	im = image.convert(mode="L")
# 	im = pil_to_np(image, mode="L")
# 	print("White ratio: ", colour_ratio(im, "White"), "Black ratio: ", colour_ratio(im, "Black"))
	if inv:
		im = invert(im)
	im = pil_to_np(im, mode="L")
	if normalize:
		white = np.max(im)
		black = np.min(im)
# 		print("white: ", white, "black: ", black)
		binary_threshold = black + (white - black) * (binary_threshold / 255)
# 	print("effective threshold: ", binary_threshold)
	im = binarize(im, binary_threshold)	
	if show: np_to_pil(im).show()
	chars = split_characters(im)
	
	return chars

def update_recognition_db(image, binary_threshold, show=True, ics=None, show_char=False, *args, **kwargs):
	recognition.update_training_set(image, ics, binary_threshold, *args, **kwargs)

# 	chars = image_characters(image, binary_threshold, show=show, *args, **kwargs)
# 	
# 	if not ics:
# 		ics = input("What are the characters in this picture? ")
# 	logger.debug("Image is supposed to have the following string: %s" % ics)
# 	
# 	if len(ics) != len(chars):
# 		logger.error(("The number of characters is not the same ("
# 			"recognized: %d, supposed to be: %d ('%s'))! Dou suru kana~ "
# 			"Skipping this image.") % (len(chars), len(ics), ics))
# 		input()
# 		return
# 
# 	for i, char in enumerate(chars):
# 		c = ics[i]
# # 		np_to_pil(char).show()
# 	
# 		if c in "0123456789":
# 			recognition.update_training_set(char, c)
# 			continue
# 		else:
# 			logger.info("Not adding char %s to the training set" % c)
# 			continue

def recognize_digits(image, binary_threshold=110, *args, **kwargs):
	return recognition.recognize_digits(image, binary_threshold, *args, **kwargs)

	### Wrappers ###

def open_image(path, grey=False, array=False):
	img = PIL.Image.open(path)
	if grey:
		img = img.convert(mode="L")
	if array:
		img = np.array(img, np.uint8)
	return img

def grab(*args, **kwargs):
	return pys.grab(*args, **kwargs)

def ocr(img):
	if img.mode != "L":
		img = img.convert(mode="L")
	return pyt.image_to_string(img)

def invert(image):
	return PIL.ImageOps.invert(image)