import logging
from time import sleep
from camera_pi2 import Camera
from servo import Servo

logger = logging.getLogger('suricate_client.' + __name__)

class Suricate:
	
	def __init__(self, id, sio):

		self.suricate_id = id
		self.sio = sio
		self.servo = Servo()
		self.current_pan = 90
		self.current_tilt = 90
		self.is_moving_cam = False
		self.camera = None
		self.stream_video = None

	def start_video_stream(self):

		logger.info("+ Starting camera...")

		self.camera = Camera(self.suricate_id, self.sio)
		
		self.camera.start_streaming()

		self.stream_video = True
		pass

	def stop_video_stream(self):

		logger.info("+ Stoping camera... ")

		if self.camera is not None:
			self.camera.stop_streaming()
		self.camera = None
		self.stream_video = False

	def start_cam_ctrl(self):
		""" Start cam motion control. 

		*shall be run in a separated thread* 
		"""

		logger.info("+ start cam ctrl")

		self.is_moving_cam = True
		self.pan_incr = 0
		self.tilt_incr = 0
		self.cam_motion()

	def stop_cam_ctrl(self):

		logger.info("+ stop cam ctrl")

		self.is_moving_cam = False

	def move_cam(self, vector):
		
		logger.debug("+ move_cam x: %.4f y: %.4f", vector['x'], vector['y'])
		
		delta = 1
		dx = vector['x'] * 2
		dy = vector['y'] * 2
		self.pan_incr = 0
		self.tilt_incr = 0

		if dx != 0:
			self.pan_incr = int(dx * (abs(dx) + delta / abs(dx)))
		if dy != 0:
			self.tilt_incr = int(dy * (abs(dy) + delta / abs(dy)))
			
		logger.debug("+ pan_incr: [%f] tilt_incr: [%f] ", self.pan_incr, self.tilt_incr)
		

	def cam_motion(self):

		while self.is_moving_cam and self.camera != None:

			pan = self.current_pan + self.pan_incr
			tilt = self.current_tilt + self.tilt_incr

			if tilt > 120:
				tilt = 120
			if tilt < 80:
				tilt = 80

			if pan > 130:
				pan = 130
			if pan < 30:
				pan = 30
		
			logger.debug("+ pan [%f] tilt [%f]", pan, tilt)
			self.servo.setServoPwm('0', pan)
			sleep(0.02)
			self.servo.setServoPwm('1', tilt)
			sleep(0.02)
			#self.camera.wait_recording(0)
			

			self.current_pan = pan
			self.current_tilt = tilt

