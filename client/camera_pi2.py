  
from picamera import PiCamera, PiVideoFrameType
from time import sleep, time_ns
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
	def __init__(self, camera, suricate_id, sio):
		logger.info('init StreamBuffer')
		self.frameTypes = PiVideoFrameType()
		self.count = 0
		self.buffer = io.BytesIO()
		self.camera = camera
		self.suricate_id = suricate_id
		self.sio = sio
		self.is_frame = False

	def write(self, buf):

		if self.camera.frame.complete and self.camera.frame.frame_type != self.frameTypes.sps_header:
			self.buffer.write(buf)
			logger.debug('end Frame nb bytes [%d]', len(self.buffer.getvalue()))
			self.frame = self.buffer.getvalue()
			time = time_ns()
			self.sio.emit('frame', { 'id' : self.suricate_id, 'time' : time, 'frame' : self.frame }, '/suricate_video_stream')
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
				logger.debug('+ Yield frame')
				yield self.frame
				
				self.is_frame = False
			else:
				sleep(0)


class Camera():

	def __init__(self, suricate_id, sio) -> None:
		self.suricate_id = suricate_id
		self.sio = sio
		self.camera = None

	def start_streaming(self):
		#with PiCamera(sensor_mode=2, resolution='500x500', framerate=30) as camera:
		self.camera = PiCamera(sensor_mode=2, resolution='500x500', framerate=30)
		
			# let camera warm up
		#sleep(2)
		streamBuffer = StreamBuffer(self.camera, self.suricate_id, self.sio)
		self.camera.start_recording(streamBuffer, **recordingOptions)
	
	def stop_streaming(self):

		self.camera.stop_recording()
		self.camera.close()

