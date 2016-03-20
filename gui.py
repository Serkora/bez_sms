import time

from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key

import game

class Game(pyglet.window.Window):
	def __init__(self, height, width):
		height = height // 2
		width = width // 2
		super().__init__(width=width, height=height, caption=('bez_sms'), 
			resizable=True, vsync=False)

		self.last_draw = 0
		self.i = 0
		self.fps_display = pyglet.clock.ClockDisplay()
		self.images = []
		self.images.append(pyglet.resource.image("images/game/s7.png"))
		self.images.append(pyglet.resource.image("images/game/s4.png"))
		for image in self.images:
			image.height = height
			image.width = width
			

			# Для тестов #
		self.time1 = time.clock()
		
	def on_draw(self):
		if (time.time() - self.last_draw) < 0.5:
			return
		self.clear()
		pyglet.gl.glClearColor(255,255,255,1)
		self.images[self.i].blit(0,0)
		self.fps_display.draw()
		self.i ^= 1
		
		self.last_draw = time.time()
	
	def on_resize(self, width, height):
		super().on_resize(width, height)
		for image in self.images:
			image.height = height
			image.width = width
		self.last_draw = 0
		


if __name__ == "__main__":
	window = Game(*game.GAME_WINDOW_SIZE)
	pyglet.clock.schedule_interval(lambda _: None, 1/150)
	pyglet.app.run()