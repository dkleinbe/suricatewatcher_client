import logging
import base64
import socketio 
from camera import Camera

logger = logging.getLogger('suricate_client.' + __name__)

class SuricateCmdNS(socketio.ClientNamespace):

	logger.info('class SuricateCmdNS')
	
	connection_count = 0

	def __init__(self, namespace, suricate_client):
		logger.info("+ Init SuricateCmdNS")
		super(socketio.ClientNamespace, self).__init__(namespace)
		
		self.suricate_client = suricate_client
		self.frame_count = 0

	def on_connect(self):
		
		SuricateCmdNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateCmdNS.connection_count)

	def on_disconnect(self):

		SuricateCmdNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateCmdNS.connection_count)

	def on_start_video_stream(self, data):
		
		logger.info("+ Recieved start_video_stream")
	
		logger.info("Geting camera... " + str(self.suricate_client.stream_video))

		self.suricate_client.camera = Camera()

		self.suricate_client.stream_video = True

	def on_stop_video_stream(self, data):
		
		
		logger.info("+ Recieved stop_video_stream")
	
		logger.info("Stoping camera... " + str(self.suricate_client.stream_video))
		self.suricate_client.camera = None
		self.suricate_client.stream_video = False
		