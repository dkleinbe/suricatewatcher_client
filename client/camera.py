import time
import logging
from base_camera import BaseCamera


class Camera(BaseCamera):
	"""An emulated camera implementation that streams a repeated sequence of
	files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
	imgs = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
	logger = logging.getLogger(__name__)

	@staticmethod
	def frames():
		count = 0
		while True:
			time.sleep(1)
			Camera.logger.info('yield img')
			yield Camera.imgs[int(time.time()) % 3]
			#yield Camera.imgs[count % 3]
			count += 1

