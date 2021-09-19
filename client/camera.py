import time
import logging
from base_camera import BaseCamera
from suricate_client import SessionId

logger = logging.getLogger('suricate_client.' + __name__)

class Camera(BaseCamera):
	"""An emulated camera implementation that streams a repeated sequence of
	files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
	imgs = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
	
	def __init__(self, suricate_id, sio) -> None:
		self.suricate_id : SessionId = suricate_id
		self.sio = sio
		self.doStream = True
	
	def start_streaming(self):
		count = 0
		while self.doStream:
			# TODO: rad a H264 stream and send it
			time.sleep(1/10)
			logger.debug('yield img')
			yield Camera.imgs[int(time.time()*10) % 3]
			#yield Camera.imgs[count % 3]
			count += 1

	def stop_streaming(self):
		self.doStream = False
