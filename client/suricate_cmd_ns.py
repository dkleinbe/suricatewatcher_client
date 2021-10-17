from __future__ import annotations
import logging
import base64
from time import sleep
import io
import socketio
from socketio import namespace 
from gpiozero import CPUTemperature, LoadAverage
import numpy as np
from ultrasonic import Ultrasonic
from ADC import Adc
from functools import reduce
import psutil

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
		self.suricate = None
		self.is_connected = False

	def on_connect_error(self, data):
		logger.critical("Connection error")

	def on_connect(self):
		
		SuricateCmdNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateCmdNS.connection_count)

		cpu = CPUTemperature()
		loadavg = LoadAverage()
		ultrasonic = Ultrasonic() 
		adc = Adc()

		self.is_connected = True
		suricate_data = {}
		nb_cpu = psutil.cpu_count()
		sample = 0
		while self.is_connected:
			
			if self.suricate is not None and self.suricate.stream_video is True:
				
	
				distance = ultrasonic.get_distance()
				left_sensor, right_sensor = adc.get_photosensors()

				suricate_data['id'] = self.suricate.suricate_id
				if sample == 0:

					load =  psutil.cpu_percent(interval=0, percpu=False)
					power = adc.get_power()

					suricate_data['cpu_temp'] = cpu.temperature
					suricate_data['cpu_load'] = load
					suricate_data['battery_power'] = power

					sample = 8
				sample -= 1

				suricate_data['distance_sensor'] = distance
				suricate_data['light_sensor'] = {'left' : left_sensor, 'right' : right_sensor}
				
				logger.debug("+ CPU Temp: %.2f, CPU load: %.2f Distance: %.2f", cpu.temperature, suricate_data['cpu_load'], distance)
				logger.debug("+ Left sensor: %.2f, Right sensor: %.2f | delta %.2f", left_sensor, right_sensor, abs(left_sensor - right_sensor))
				logger.debug("+ Power: %.2f V", suricate_data['battery_power'])

				self.suricate_client.sio.emit('suricate_data', suricate_data , '/suricate_cmd')

			sleep(0.25)



	def on_disconnect(self):

		SuricateCmdNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateCmdNS.connection_count)

		self.is_connected =False
		#
		# if we were streaming, free the camera
		#
		if self.suricate is not None:
			self.suricate.stop_video_stream()	

	def on_suricate_id(self, msg):

		logger.info("+ Recieved suricate_id")
		# TODO: move suricate to Client: self.suricate_client.suricate = ...
		self.suricate = Suricate(msg['suricate_id'], self.suricate_client.sio)

	def on_start_video_stream(self, data):
		
		logger.info("+ Recieved start_video_stream")

		if self.suricate is not None:
			self.suricate.start_video_stream()

	def on_stop_video_stream(self, data):
		
		logger.info("+ Recieved stop_video_stream")

		if self.suricate is not None:
			self.suricate.stop_video_stream()


	def on_start_cam_ctrl(self, data):

		logger.info("+ Recieved start cam ctrl")

		if self.suricate is not None:
			self.suricate.start_cam_ctrl()

	def on_stop_cam_ctrl(self, data):

		logger.info("+ Recieved stop cam ctrl")

		if self.suricate is not None:
			self.suricate.stop_cam_ctrl()

	def on_move_cam(self, vector):
		
		logger.debug("+ Recieved move_cam x: %.4f y: %.4f", vector['x'], vector['y'])
		
		if self.suricate is not None:
			self.suricate.move_cam(vector)
		



