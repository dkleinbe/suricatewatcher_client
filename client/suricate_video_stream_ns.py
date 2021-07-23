import logging
import base64
import socketio 

logger = logging.getLogger('suricate_client.' + __name__)

class SuricateVideoStreamNS(socketio.ClientNamespace):

	logger.info('class SuricateVideoStreamNS')
	
	connection_count = 0

	def __init__(self, namespace):
		logger.info("+ Init SuricateVideoStreamNS")
		super(socketio.ClientNamespace, self).__init__(namespace)
		
		self.frame_count = 0

	def on_connect(self):
		
		SuricateVideoStreamNS.connection_count += 1

		logger.info("+ %s: connection: %d", self.namespace, SuricateVideoStreamNS.connection_count)

	def on_disconnect(self):

		SuricateVideoStreamNS.connection_count -= 1

		logger.info("+ %s: disconnect: %d", self.namespace, SuricateVideoStreamNS.connection_count)

	


		