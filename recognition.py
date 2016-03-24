import os
import time
import pickle

import graphics

from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import TanhLayer, SoftmaxLayer

import logging					# ugly fix
logging.root.handlers = []		# ugly fix
from logger import Logger
logger = Logger(__name__, Logger.INFO)

NET_PATH = 'neural/nnet_digits.pickle'
TRAINING_SET_PATH = 'neural/nnet_digits_training.pickle'

INPUTS = 25
OUTPUTS = 10

NETWORK = None
TRAINING_SET = None

def build_network(inputs=INPUTS, layers=3, outputs=OUTPUTS, bias=False, *args, **kwargs):
	logger.info("Creating a new network")
	net = buildNetwork(inputs, layers, outputs, bias=bias, *args, **kwargs)
# 	net.training_set = SupervisedDataSet(inputs, outputs)
	return net

def get_network(path=NET_PATH, *args, **kwargs):
	if os.path.isfile(path):# and False:
		logger.info("Loading the network from disk.")
		with open(path, 'rb') as f:
			net = pickle.load(f)
		net.sorted = False
		net.sortModules()
		logger.info("Length of the training set: %d" % len(net.training_set))
	else:
		net = build_network(*args, **kwargs)
		
	return net

def update_training_set(image, digits=None, binary_threshold=110, net=None, new=False):
	if not net:
		net = NETWORK
	if new:
		training_set = SupervisedDataSet(INPUTS, OUTPUTS)
	elif not TRAINING_SET:
		if os.path.isfile(TRAINING_SET_PATH):
			with open(TRAINING_SET_PATH, 'rb') as f:
				training_set = pickle.load(f)
		else:
			training_set = SupervisedDataSet(INPUTS, OUTPUTS)
	else:
		training_set = TRAINING_SET
		
	if not digits:
		image.show()
		digits = input("What are the characters in this picture? ")
	logger.debug("Image is supposed to have the following string: %s" % digits)
	
	if len(digits) == 1:
		chars = [image]
	else:
		chars = graphics.image_characters(image, binary_threshold)
	
	if len(digits) != len(chars):
		logger.error(("The number of characters is not the same ("
			"recognized: %d, supposed to be: %d ('%s'))! Dou suru kana~ "
			"Skipping this image.") % (len(chars), len(digits), digits))
		input()
		return
	
	for i, char in enumerate(chars):
		d = digits[i]
		if d not in "0123456789":
			logger.debug("Not adding char %s to the training set" % d)
			continue
		inputs = graphics.pil_to_np(char.resize((5,5), 1)).flatten()
		outputs = [0] * 10
		outputs[int(d)] = 1
		training_set.addSample(inputs, outputs)
		logger.debug("Added a sample for digits %s. Training set size: %d" % (d, len(training_set)))
	
	with open(TRAINING_SET_PATH, 'wb') as f:
		pickle.dump(training_set, f)
	

def train(reps, training_set=None, net=None):
	if not net:
		net = NETWORK
	if not training_set:
		training_set = TRAINING_SET

	trainer = BackpropTrainer(net, training_set)
	logger.info("Benkyou benkyou benkyou...")
	for i in range(reps):
		c = trainer.train()
		if i % 10 == 0:
			print("Epoch %3d, error: %.5f" % c)

def is_digit(char):
	return True

def recognize_digits(image, binary_threshold=110, show=False, *args, **kwargs):
	if show:
		image.show()
	chars = graphics.image_characters(image, binary_threshold)
	digits = ""
	for char in chars:
		char = graphics.crop_to_bounding_box(char)
		if not is_digit(char):
			digits += recognize_char(char)
			continue
		char = char.resize((5,5), 1)
		inputs = graphics.pil_to_np(char).flatten()
		output = NETWORK.activate(inputs)
		top = output.argmax()
		digits += str(top)
		
		second = output.argpartition(-2)[-2:-1][0]
		
		logger.debug("Top two values: %.3f (%s), %.3f (%s). Ratio: %.3f" % (
			output[top], str(top), output[second], str(second),
			output[second]/output[top]))
	return digits

def recognize_char(image):
	return "."
	
NETWORK = get_network(layers=25, bias=True, hiddenclass=TanhLayer, outclass=SoftmaxLayer)

# z = np.zeros(25, dtype=np.uint8)
# o = np.ones(25, dtype=np.uint8)

# update_training_set(NETWORK, z, 0)
# update_training_set(NETWORK, o, 1)

# create_dataset()
# train(NETWORK, 50)
# test()