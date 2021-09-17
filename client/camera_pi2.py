  
from picamera import PiCamera, PiVideoFrameType
from time import sleep
from itertools import cycle
import logging
import io

from base_camera import BaseCamera


recordingOptions = {
	'format' : 'h264', 
	'quality' : 20, 
	'profile' : 'high', 
	'level' : '4.2', 
	'intra_period' : 15, 
	'intra_refresh' : 'both', 
	'inline_headers' : True, 
	'sps_timing' : True
}

logger = logging.getLogger('suricate_client.' + __name__)

class StreamBuffer(object):
	def __init__(self,camera):
		logger.info('init StreamBuffer')
		self.frameTypes = PiVideoFrameType()
		self.count = 0
		self.buffer = io.BytesIO()
		self.camera = camera
		self.is_frame = False

	def write(self, buf):

		if self.camera.frame.complete and self.camera.frame.frame_type != self.frameTypes.sps_header:
			self.buffer.write(buf)
			#logger.debug('end Frame nb bytes [%d]', len(self.buffer.getvalue()))
			self.frame = self.buffer.getvalue()
			
			self.buffer.seek(0)
			self.buffer.truncate()
			
			self.is_frame = True
			self.count += 1

		else:
			self.buffer.write(buf)
			logger.debug('write')
			
	
	def frames(self):
		
		while True:
			if (self.is_frame):
				yield self.frame
				
				self.is_frame = False


class Camera(BaseCamera):

	@staticmethod
	def frames():
		#
		with PiCamera(sensor_mode=2, resolution='800x800', framerate=30) as camera:
		
			# let camera warm up
	        #sleep(3)
			streamBuffer = StreamBuffer(camera)
			camera.start_recording(streamBuffer, **recordingOptions)

			for frame in streamBuffer.frames():
				yield frame

	def start_streaming(self):
		#with PiCamera(sensor_mode=2, resolution='500x500', framerate=30) as camera:
		camera = PiCamera(sensor_mode=2, resolution='500x500', framerate=30)
			# let camera warm up
		#sleep(2)
		streamBuffer = StreamBuffer(camera)
		camera.start_recording(streamBuffer, **recordingOptions)

			#for frame in streamBuffer.frames():
			#	yield frame

if __name__ == '__main__':
	# 1920x1080
	camera = PiCamera(sensor_mode=2, resolution='100x100', framerate=30)
	camera.video_denoise = False

	try:
		streamBuffer = StreamBuffer(camera)
		print('start_recording')
		sleep(2)
		camera.start_recording(streamBuffer, **recordingOptions) 
		count = 0
		for frame in streamBuffer.frames():
			print('Got a frame')
		
		if False:
			for stream in camera.record_sequence(
				cycle((StreamBuffer(camera), StreamBuffer(camera))), 
				**recordingOptions):
				print('record: ', count)
				count += 1
				camera.wait_recording(2)
		while True:
			#sleep(0.2)
			pass

	except KeyboardInterrupt:
		camera.stop_recording()
		camera.close()
	