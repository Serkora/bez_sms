# -*- coding: utf-8 -*-

import random
import argparse


class Game(object):
	def __init__(self, turn=None, player_hand=None, comp_hand=None, table=None, rate=None):
		self.turn = player_turn
		self.turn_count = 1
		self.player_hand = list([dice_throw() for i in range(2)])
		self.comp_hand = list([dice_throw() for i in range(2)])
		self.table = list([dice_throw() for i in range(3)])
		self.rate = False



def player_turn(game):
	print('Your hand: ', game.player_hand)
	print('Pass/', ((game.rate==False and 'Raise') or ('Call')))
	res = (input() and True) or False
	print((res==True and 'Raise') or 'Pass')
	return [comp_turn, res]

def comp_turn(game):
	print('Computer...')
	choice = random.random()
	res = (choice>0.5 and 'Raise') \
	or ('Pass')
	print(res)
	return [player_turn, (choice>0.5 and \
	True) or False]

def flop(game):
	print('Table cards: ', game.table)

def end(game):
	print('End!')
	flop(game)
	print('Your cards: ', game.player_hand)
	print('Computer cards: ', game.comp_hand)

def dice_throw():
	return random.choice([i for i in range(1,7)])

def main(game):
	print('Turn ', game.turn_count)
	res = game.turn(game)
	(game.turn_count == 2 and flop(game))
	if game.turn_count == 4:
		end(game)
	else:
		game.turn = res[0]
		game.rate = res[1]
		game.turn_count += 1
		main(game)

game1 = Game()
main(game1)