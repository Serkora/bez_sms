import graphics
import numpy as np

def colour_ratio_rgb(array, col, offset=(0,0), size=None, w_thres=None,
		*args, **kwargs):
	if len(array.shape) == 2:
		array.reshape(1, array.shape[0], array.shape[1])
	if type(col) == str:
		col = ["Red", "Green", "Blue"].index(col)
	total = 0
	colour = 0
	if size:
		height = min(size[0], array.shape[0])
		width = min(size[1], array.shape[0])
	else:
		height = array.shape[0] - offset[0]
		width = array.shape[1] - offset[1]

	for i in range(height):
		for j in range(width):
			t = sum(array[i+offset[0]][j+offset[1]][:3])
			if w_thres and t > w_thres: continue		# ignore "white" pixels
			total += t
			colour += array[i+offset[0]][j+offset[1]][col]
	print("Total: %d, colour: %d" % (total, colour))
	return colour / max(total,0.001)
	
def colour_ratio_rgb_opt(array, col, offset=(0,0), size=None, w_thres=None,
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
# 	if w_thres:
# 		for row in slice:
# 			for pixel in row:
# 				if np.sum(pixel[:3]) > w_thres:
# 					pixel[:3] = np.array([0,0,0])
	if w_thres:
		slice = slice[np.sum(slice, axis=2) <= w_thres]
		colour = np.sum(slice[:,col])
# 		total = np.sum(np.sum(slice[:,:], axis=2) <= w_thres)
# 		colour = np.sum(np.sum(slice[:,:], axis=2) <= w_thres)
	else:
		colour = np.sum(slice[:,:,col])

	total = np.sum(slice)	
# 	print(slice[:,:,:3] > w_thres)
	

# 	for i in range(height):
# 		for j in range(width):
# 			t = sum(array[i+offset[0]][j+offset[1]][:3])
# 			if w_thres and t > w_thres: continue		# ignore "white" pixels
# 			total += t
# 			colour += array[i+offset[0]][j+offset[1]][col]
	print("Total: %d, colour: %d" % (total, colour))
	return colour / max(total, 0.00001)

im = graphics.open_image("images/cards/2d.png")
im.show()

im_np = graphics.pil_to_np(im)

print(colour_ratio_rgb(im_np, "Red", offset=(5,7), size=(4,4), w_thres=None))
print(colour_ratio_rgb_opt(im_np, "Red", offset=(5,7), size=(4,4), w_thres=None))