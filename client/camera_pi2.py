  

from typing import List, NewType, Optional, Union, Any
from time import sleep, time_ns
import logging
import io
from picamera import PiCamera, PiVideoFrameType

from base_camera import BaseCamera

SessionId = NewType('SessionId', str)

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

		logger.info('+ Init StreamBuffer')
		self.frameTypes = PiVideoFrameType()
		self.count = 0
		self.buffer = io.BytesIO()
		self.camera = camera
		self.suricate_id = suricate_id
		self.sio = sio
		self.is_frame = False

	def write(self, buf):

		if self.camera.frame.complete and self.camera.frame.frame_type != self.frameTypes.sps_header:

			logger.debug('+ end of Frame ')

			self.buffer.write(buf)
			
			time = time_ns()
			self.sio.emit('frame', { 'id' : self.suricate_id, 'time' : time, 'frame' : self.buffer.getvalue() }, '/suricate_video_stream')

			self.buffer.seek(0)
			self.buffer.truncate()
			
			self.is_frame = True
			self.count += 1

		else:
			self.buffer.write(buf)
			logger.debug('+ write part of frame')
			

class Camera(BaseCamera):

	def __init__(self, suricate_id, sio) -> None:
		self.suricate_id : SessionId = suricate_id
		self.sio = sio
		self.camera : Optional[PiCamera] = None

	def start_streaming(self):
		
		logger.info('+ Start streaming')
		self.camera = PiCamera(sensor_mode=2, resolution='500x500', framerate=30)
		
			# let camera warm up
		#sleep(2)
		streamBuffer = StreamBuffer(self.camera, self.suricate_id, self.sio)
		self.camera.start_recording(streamBuffer, **recordingOptions)
	
	def stop_streaming(self):

		if self.camera is not None:

			logger.info('+ Stop streaming')
			
			self.camera.stop_recording()
			self.camera.close()

