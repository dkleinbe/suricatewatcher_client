from __future__ import annotations
import logging
import base64
from time import sleep
import io
import socketio
from socketio import namespace 
from gpiozero import CPUTemperature, LoadAverage
import numpy as np

from suricate import Suricate
from camera_pi2 import Camera

import typing
if typing.TYPE_CHECKING:
	from suricate_client import Client

logger = logging.getLogger('suricate_client.' + __name__)

class SuricateCmdNS(socketio.ClientNamespace):

	logger.debug('class SuricateCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_client : Client):

		logger.info("+ Init SuricateCmdNS")

		super(socketio.ClientNamespace, self).__init__(namespace)
		
		self.suricate_client = suricate_client

	def on_connect_error(self, data):
		logger.critical("Connection error")

	def on_connect(self):
		
		SuricateCmdNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateCmdNS.connection_count)

		cpu = CPUTemperature()
		loadavg = LoadAverage()
		while True:
			
			with io.open(loadavg.load_average_file, 'r') as f:

				file_columns = f.read().strip().split()
				load = float(file_columns[loadavg._load_average_file_column])

			logger.debug("+ CPU Temp: %.2f, CPU load: %.2f", cpu.temperature, load)
			sleep(1)



	def on_disconnect(self):

		SuricateCmdNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateCmdNS.connection_count)
		#
		# if we were streaming, free the camera
		#
		self.suricate.stop_video_stream()	

	def on_suricate_id(self, msg):

		logger.info("+ Recieved suricate_id")

		self.suricate = Suricate(msg['suricate_id'], self.suricate_client.sio)

	def on_start_video_stream(self, data):
		
		logger.info("+ Recieved start_video_stream")

		self.suricate.start_video_stream()

	def on_stop_video_stream(self, data):
		
		logger.info("+ Recieved stop_video_stream")

		self.suricate.stop_video_stream()


	def on_start_cam_ctrl(self, data):

		logger.info("+ Recieved start cam ctrl")

		self.suricate.start_cam_ctrl()

	def on_stop_cam_ctrl(self, data):

		logger.info("+ Recieved stop cam ctrl")

		self.suricate.stop_cam_ctrl()

	def on_move_cam(self, vector):
		
		logger.debug("+ Recieved move_cam x: %.4f y: %.4f", vector['x'], vector['y'])
		
		self.suricate.move_cam(vector)
		



