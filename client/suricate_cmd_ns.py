from __future__ import annotations
import logging
import base64
import socketio
from socketio import namespace 
from camera_pi2 import Camera
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

	def on_connect_error(self, data):
		logger.critical("Connection error")

	def on_connect(self):
		
		SuricateCmdNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateCmdNS.connection_count)

	def on_disconnect(self):

		SuricateCmdNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateCmdNS.connection_count)

	def on_suricate_id(self, msg):

		logger.info("+ Recieved suricate_id")

		self.suricate_client._suricate_id = msg['suricate_id']

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

	def on_start_cam_ctrl(self, data):

		logger.info("+ Recieved start cam ctrl")

	def on_stop_cam_ctrl(self, data):

		logger.info("+ Recieved stop cam ctrl")
			
	def on_move_cam(self, data):

		logger.info("+ Recieved move_cam")
		