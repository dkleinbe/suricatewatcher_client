from typing import List, NewType, Optional, Union, Any
import argparse
import coloredlogs, logging
import logging.config
import json
from os import name
from time import sleep, time_ns
import socketio
from socketio import exceptions
from base_camera import BaseCamera
from suricate_video_stream_ns import SuricateVideoStreamNS
from suricate_cmd_ns import SuricateCmdNS


with open('logger_conf2.json') as json_file:
	conf = json.load(json_file)
logging.config.dictConfig(conf['logging'])

my_logger = logging.getLogger('suricate_client')

my_logger.debug('Logger debug')
my_logger.info('Logger init done')
my_logger.warning('Logger warning')
my_logger.error('Logger error')
my_logger.critical('Logger critical')

my_logger.info("LAUNCHING APP")


SessionId = NewType('SessionId', str)
CamType =  Optional[BaseCamera]

class Client:
	def __init__(self):
					
		self._suricate_id : SessionId = SessionId('NOT_SET')
		self._stream_video = False
		self._camera      : CamType = None
		self.sio = socketio.Client(logger=False, engineio_logger=False)
		
		self.sio.register_namespace(SuricateVideoStreamNS('/suricate_video_stream'))
		self.sio.register_namespace(SuricateCmdNS('/suricate_cmd', suricate_client=self))

		connected = False
		while not connected:
			try:
				self.sio.connect(host, auth= { 'id' : self._suricate_id }, namespaces=['/suricate_video_stream', '/suricate_cmd'])
			except exceptions.ConnectionError as err:
				my_logger.error("+ ConnectionError: %s", err)
			else:
				my_logger.info("+ Connected")
				connected = True
				
		#self.sio.connect(host, auth= { 'id' : self._suricate_id }, namespaces=['/suricate_video_stream', '/suricate_cmd'])


	@property
	def id(self):
		my_logger.debug('+ Getting suricate camera: ' + str(self._suricate_id))
		return self._suricate_id
	
	@id.setter
	def id(self, id):
		my_logger.debug('+ Setting suricate camera: ' + str(id))
		self._suricate_id = id	
# TODO: remove camera and stream_video properties if not needed
	@property
	def camera(self) -> CamType:
		my_logger.debug('+ Getting suricate camera: ' + str(self._camera))
		return self._camera
	
	@camera.setter
	def camera(self, cam : CamType):
		my_logger.debug('+ Setting suricate camera: ' + str(cam))
		self._camera = cam	

	@property
	def stream_video(self):
		my_logger.debug('+ Getting suricate stream_video: ' + str(self._stream_video))
		return self._stream_video
	
	@stream_video.setter
	def stream_video(self, stream):
		my_logger.debug('+ Setting suricate stream_video: ' + str(stream))
		self._stream_video = stream	

	def run(self):
		
		self.sio.wait()

	def stop(self):

		self.sio.disconnect()

parser = argparse.ArgumentParser()
parser.add_argument("-host", help="host to connecto: http://host:port")
args = parser.parse_args()
if args.host:
	host = args.host
else:
	exit()


client = Client()

try:

	client.run()

except KeyboardInterrupt:
	my_logger.info("+ Terminated ")
	client.stop()


my_logger.critical("I'm dead meat.........")
