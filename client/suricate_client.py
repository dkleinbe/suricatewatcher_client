import argparse
import logging
import logging.config
from os import name
from time import sleep
import socketio
from camera import Camera
from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_ns import SuricateCmdNS

logging.config.fileConfig('logger.conf',disable_existing_loggers=False)

my_logger = logging.getLogger('suricate_client')


my_logger.info("LAUNCHING APP")

class Client:
	def __init__(self):

		self._id = 'NOT_SET'
		self._stream_video = False
		self._camera = None
		self.sio = socketio.Client(logger=False, engineio_logger=False)

		my_logger.info("Connecting to host: [%s]", host)

		self.sio.register_namespace(SuricateVideoStreamNS('/suricate_video_stream'))
		self.sio.register_namespace(SuricateCmdNS('/suricate_cmd', suricate_client=self))


		self.sio.connect(host, auth= { 'id' : self._id }, namespaces=['/suricate_video_stream', '/suricate_cmd'])

		

	@property
	def id(self):
		my_logger.info('+ Getting suricate camera: ' + str(self._id))
		return self._id
	
	@id.setter
	def camera(self, id):
		my_logger.info('+ Setting suricate camera: ' + str(id))
		self._id = id	

	@property
	def camera(self):
		my_logger.info('+ Getting suricate camera: ' + str(self._camera))
		return self._camera
	
	@camera.setter
	def camera(self, cam):
		my_logger.info('+ Setting suricate camera: ' + str(cam))
		self._camera = cam	

	@property
	def stream_video(self):
		my_logger.info('+ Getting suricate stream_video: ' + str(self._stream_video))
		return self._stream_video
	
	@stream_video.setter
	def stream_video(self, stream):
		my_logger.info('+ Setting suricate stream_video: ' + str(stream))
		self._stream_video = stream	

	def run(self):
		
		while True:

			my_logger.info("Waiting... ")
			sleep(1)

			if self.stream_video == True:
				my_logger.info("Frame")

				frame = self.camera.get_frame()
				try:
					self.sio.emit('frame', { 'id' : self._id, 'frame' : frame }, '/suricate_video_stream')
			
				except:
					my_logger.exception("- Can't emit frame")
					self.stream_video = False

			else:
				sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument("-host", help="host to connecto: http://host:port")
args = parser.parse_args()
if args.host:
	host = args.host
else:
	exit()


client = Client()

client.run()

my_logger.info("I'm dead meat.........")
