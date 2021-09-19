from typing import Generator, List, Optional
import time
import logging


class BaseCamera(object):
	
	logger = logging.getLogger('suricate_client.' + __name__)
	

	def __init__(self):
		pass
	
	def start_streaming(self):
		""" create camera and start streaming """
		raise RuntimeError('Must be implemented by subclasses.')

	def stop_streaming(self):
		""" stop streaming and close camera """
		raise RuntimeError('Must be implemented by subclasses.')

		