import random

from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import TanhLayer, SoftmaxLayer
import graphics
import numpy as np
import pickle
import os
import time

NET_PATH = 'nnet'

def build_network(inputs=25, layers=3, outputs=10, bias=False, *args, **kwargs):
	print("Creating a new network")
	net = buildNetwork(inputs, layers, outputs, bias=bias, *args, **kwargs)
	net.training_set = SupervisedDataSet(inputs, outputs)
	return net

def get_network(path=NET_PATH, *args, **kwargs):
	if os.path.isfile(path):# and False:
		print("Loading the network from disk.")
		with open(path, 'rb') as f:
			net = pickle.load(f)
		net.sorted = False
		net.sortModules()
		print("Length of the training set: %d" % len(net.training_set))
	else:
		net = build_network(*args, **kwargs)
		
	return net

def update_training_set(image, digit, net=None, new=False):
	if not net:
		net = NETWORK
	if new or not hasattr(net, 'training_set'):
		net.training_set = SupervisedDataSet(net.training_set.indim, net.training_set.outdim)
	image = graphics.np_to_pil(image)
	image = graphics.crop_to_bounding_box(image)
# 	image.show()
	image = image.resize((5,5), 1)
# 	image.show()
	outputs = [0]*10
	outputs[int(digit)] = 1
	inputs = graphics.pil_to_np(image).flatten()
# 	print("Digit: %s" % digit)
# 	print("inputs: ", inputs)
# 	print("outputs: ", outputs)
	net.training_set.addSample(inputs, outputs)
	print("Added a sample for digits %s. Training set size: %d" % (digit, len(net.training_set)))

def train(reps, net=None):
	if not net:
		net = NETWORK
	trainer = BackpropTrainer(net, net.training_set)
	print("Benkyou benkyou benkyou...")
	for i in range(reps):
		c = trainer.train()
		if i % 10 == 0:
			print("Error: %.5f" % c)

def recognize_digits(image, binary_threshold=110, *args, **kwargs):
	image.show()
	chars = graphics.image_characters(image, binary_threshold)
	digits = ""
	for char in chars:
		char = graphics.crop_to_bounding_box(char)
# 		char.show()
		char = char.resize((5,5), 1)
		inputs = graphics.pil_to_np(char).flatten()
# 		print(inputs)
		r = NETWORK.activate(inputs)
# 		print(r)
		digits += str(r.argmax())
# 		input("digits so far: %s" % digits)
# 	print("Digits recognized: %s" % digits)
	return digits

def create_dataset():
	for i in range(500):
		ones = random.randint(0,25)
		ds = [1]*ones + [0]*(25-ones)
		random.shuffle(ds)
		update_training_set(NETWORK, ds, int(ones > 12))

def test():
	t = time.time()
	c = 0
	for i in range(1000):
		ones = random.randint(0,25)
		ds = [1]*ones + [0]*(25-ones)
		random.shuffle(ds)
		r = NETWORK.activate(ds)[0]
		if (int(ones > 12) == round(r)):
			c += 1
		
	print("Network is correct %.3f%% of the time." % (c / 10))
	print("Took %.3f seconds." % (time.time() - t))
	
NETWORK = get_network(layers=25, bias=True, hiddenclass=TanhLayer, outclass=SoftmaxLayer)

# z = np.zeros(25, dtype=np.uint8)
# o = np.ones(25, dtype=np.uint8)

# update_training_set(NETWORK, z, 0)
# update_training_set(NETWORK, o, 1)

# create_dataset()
# train(NETWORK, 50)
# test()