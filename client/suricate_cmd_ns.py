from __future__ import annotations
import logging
import base64
from time import sleep
import socketio
from socketio import namespace 
import numpy as np
from camera_pi2 import Camera
from servo import Servo
import typing
if typing.TYPE_CHECKING:
	from suricate_client import Client

logger = logging.getLogger('suricate_client.' + __name__)

class SuricateCmdNS(socketio.ClientNamespace):

	logger.info('class SuricateCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_client : Client):
		logger.info("+ Init SuricateCmdNS")
		super(socketio.ClientNamespace, self).__init__(namespace)
		
		self.suricate_client = suricate_client
		self.frame_count = 0
		self.servo = Servo()
		self.current_pan = 90
		self.current_tilt = 90
		self.is_moving_cam = False

	def on_connect_error(self, data):
		logger.critical("Connection error")

	def on_connect(self):
		
		SuricateCmdNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateCmdNS.connection_count)

	def on_disconnect(self):

		SuricateCmdNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateCmdNS.connection_count)
		#
		# if we were streaming, free the camera
		#
		if self.suricate_client.camera is not None:
			self.suricate_client.camera.stop_streaming()
		self.suricate_client.camera = None
		self.suricate_client.stream_video = False		

	def on_suricate_id(self, msg):

		logger.info("+ Recieved suricate_id")

		self.suricate_client._suricate_id = msg['suricate_id']

	def on_start_video_stream(self, data):
		
		logger.info("+ Recieved start_video_stream")
		logger.info("+ Geting camera... " + str(self.suricate_client.stream_video))

		self.suricate_client.camera = Camera(self.suricate_client._suricate_id, self.suricate_client.sio)
		self.suricate_client.camera.start_streaming()

		self.suricate_client.stream_video = True

	def on_stop_video_stream(self, data):
		
		
		logger.info("+ Recieved stop_video_stream")
		logger.info("+ Stoping camera... " + str(self.suricate_client.stream_video))

		if self.suricate_client.camera is not None:
			self.suricate_client.camera.stop_streaming()
		self.suricate_client.camera = None
		self.suricate_client.stream_video = False


	def on_start_cam_ctrl(self, data):

		logger.info("+ Recieved start cam ctrl")
		self.is_moving_cam = True
		self.pan_incr = 0
		self.tilt_incr = 0
		self.cam_motion()

	def on_stop_cam_ctrl(self, data):

		logger.info("+ Recieved stop cam ctrl")

		self.is_moving_cam = False
			
	def on_move_cam_old(self, vector):
		
		logger.debug("+ Recieved move_cam x: %.4f y: %.4f", vector['x'], vector['y'])
		
		if self.is_moving_cam is True:
			logger.info('+ Ignoring cam move')
			return

		delta = 0.1
		pan = 90 * vector['x'] + 90
		tilt = 90 * vector['y'] + 90
		if tilt > 120:
			tilt = 120
		if tilt < 75:
			tilt = 75

		if pan > 130:
			pan = 130
		if pan < 30:
			pan = 30
			
		#pan = int(round(pan))
		#tilt = int(round(tilt))
		current_pan = self.current_pan
		current_tilt = self.current_tilt

		apan = iter(())
		atilt = iter(())

		num_pan = abs((current_pan - pan) / delta)
		num_tilt = abs((current_tilt - tilt) / delta)

		num = max(num_pan, num_tilt)
		if num_pan >= 1 :
			apan = np.nditer(np.linspace(current_pan, pan, num))
		if num_tilt >= 1 :
			atilt = np.nditer(np.linspace(current_tilt, tilt, num))
		
		logger.info("+ Pan: %.4f(%f) Tilt: %.4f(%f)", pan, num_pan, tilt, num_tilt)

		if self.is_moving_cam is not True:
			self.is_moving_cam = True
			p = next(apan, False)
			t = next(atilt, False)
			while p or t:
				
				if p:
					logger.info("+ setServoPwm('0', %f", p)
					self.servo.setServoPwm('0', p)
					self.current_pan = p

				if t:
					logger.info("+ setServoPwm('1', %f", t)
					self.servo.setServoPwm('1', t)
					self.current_tilt = t

				sleep(0.001)
				 
				p = next(apan, False)
				t = next(atilt, False)

			self.is_moving_cam = False
		else:
			logger.info('+ Ignoring cam move')

	def on_move_cam(self, vector):
		
		logger.debug("+ Recieved move_cam x: %.4f y: %.4f", vector['x'], vector['y'])
		
		delta = 0.01
		dx = vector['x']
		dy = vector['y']
		self.pan_incr = 0
		self.tilt_incr = 0

		if dx != 0:
			self.pan_incr = dx * (abs(dx) + delta / abs(dx))
		if dy != 0:
			self.tilt_incr = dy * (abs(dy) + delta / abs(dy))
			
		logger.info("+ pan_incr: [%f] tilt_incr: [%f] ", self.pan_incr, self.tilt_incr)
		

	def cam_motion(self):

		while self.is_moving_cam:

			pan = self.current_pan + self.pan_incr
			tilt = self.current_tilt + self.tilt_incr

			if tilt > 120:
				tilt = 120
			if tilt < 75:
				tilt = 75

			if pan > 130:
				pan = 130
			if pan < 30:
				pan = 30
		
			self.servo.setServoPwm('0', pan)
			self.servo.setServoPwm('1', tilt)
			self.suricate_client.camera.camera.wait_recording(0)
			#sleep(0.05)

			self.current_pan = pan
			self.current_tilt = tilt

