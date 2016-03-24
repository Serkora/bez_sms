import os
import time
import logging

class Logger(object):
	DEBUG = logging.DEBUG
	INFO = logging.INFO
	WARNING = logging.WARNING
	ERROR = logging.ERROR
	CRITICAL = logging.CRITICAL

	def __init__(self, name=None, level=DEBUG):
		self.logger = logging.getLogger(name)
		self.logger.setLevel(self.DEBUG)
		self.formatter = logging.Formatter('%(name)-12s [%(levelname).1s]: %(message)s')
		self.fhandler = logging.FileHandler('log.log')
		self.chandler = logging.StreamHandler()
		self.fhandler.setLevel(level)
		self.chandler.setLevel(level)
		self.fhandler.setFormatter(self.formatter)
		self.chandler.setFormatter(self.formatter)
# 		self.logger.addHandler(self.fhandler)
		self.logger.addHandler(self.chandler)
	
	def setLevel(self, level, handler=None, *args, **kwargs):
		self.logger.setLevel(level, *args, **kwargs)
		if handler:
			handler.setLevel(level)
		else:
			for handler in self.logger.handlers:
				handler.setLevel(level)
	def debug(self, message, *args, **kwargs):
		self.logger.debug(message, *args, **kwargs)
	
	def info(self, message, *args, **kwargs):
		self.logger.info(message, *args, **kwargs)
		
	def warning(self, message, *args, **kwargs):
		self.logger.warning(message, *args, **kwargs)
	
	def error(self, message, *args, **kwargs):
		self.logger.error(message, *args, **kwargs)
	
	def critical(self, message, *args, **kwargs):
		self.logger.critical(message, *args, **kwargs)
	
# logger = Logger()
# logger.setLevel(Logger.DEBUG)