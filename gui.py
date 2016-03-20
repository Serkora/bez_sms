import time

from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key

from threading import Thread

import game

class Game(pyglet.window.Window):
	def __init__(self, height, width):
		height = height // 2
		width = width // 2
		super().__init__(width=width, height=height, caption=('bez_sms'), 
			resizable=True, vsync=False)

		self.last_update = 0
		self.i = 0
		self.fps_display = pyglet.clock.ClockDisplay()
# 		self.images = []
# 		self.images.append(pyglet.resource.image("images/game/s7.png"))
# 		self.images.append(pyglet.resource.image("images/game/s4.png"))
# 		for image in self.images:
# 			image.height = height
# 			image.width = width
		self.updating = False
		self.update_image(join=True)
		self.image = self.next_image.get_texture()

			# Для тестов #
		self.time1 = time.clock()
	
	def update_image(self, join=False):
# 		print("update_image called")
		if self.updating: return
		
		self.updating = True
		thr = Thread(target=self._update_image, args=())
		thr.start()
		if join:
			thr.join()
# 		self._update_image()
	
	def _update_image(self):
# 		print("started _update_image")
		pil_image = game.create_image_with_info()
		pil_image.save("tmp.png")
# 		print("saved to file")
		image = pyglet.image.load("tmp.png")
# 		print("loaded from file")
# 		image.height = self.height
# 		image.width = self.width
# 		print("changed size")
		self.next_image = image
		self.updating = False
# 		print("finished _update_image")
	
	def on_draw(self):
		if (time.time() - self.last_update) > 0.1:
			self.update_image()
			self.last_update = time.time()
		self.clear()
		pyglet.gl.glClearColor(255,255,255,1)
# 		pil_image = game.create_image_with_info()
# 		pil_image.save("tmp.png")
# 		image = pyglet.resource.image("tmp.png")
# 		image.height = self.height
# 		image.width = self.width
		self.image.blit(0,0)
		self.image = self.next_image.get_texture()
		self.resize_image()
# 		self.images[self.i].blit(0,0)
		self.fps_display.draw()
# 		self.i ^= 1

	def resize_image(self):
		self.image.height = self.height
		self.image.width = self.width
		self.next_image = self.image
	
	def on_resize(self, width, height):
		super().on_resize(width, height)
		self.resize_image()
# 		self.image.height = self.height
# 		self.image.width = self.width
# 		self.next_image = self.image
# 		for image in self.images:
# 			image.height = height
# 			image.width = width
# 		self.last_draw = 0
		


if __name__ == "__main__":
	window = Game(*game.GAME_WINDOW_SIZE)
	pyglet.clock.schedule_interval(lambda _: None, 1/150)
	pyglet.app.run()