import argparse
import logging
import logging.config
from os import name
import socketio
from camera import Camera


logging.config.fileConfig('logger.conf',disable_existing_loggers=False)

my_logger = logging.getLogger('suricate_client')

# 'application' code
my_logger.debug('debug message')
my_logger.info('info message')
my_logger.warning('warn message')
my_logger.error('error message')
my_logger.critical('critical message')

my_logger.info("LAUNCHING APP")

sio = socketio.Client(logger=False, engineio_logger=False)


@sio.event(namespace='/video_stream')
def connect():
	my_logger.info("I'm connected! to /video_stream")
	
@sio.event(namespace='/cmd_suricate')
def connect():
	my_logger.info("I'm connected! to /cmd_suricate")
	

@sio.event
def connect_error(data):
	print("The connection failed!")
	exit()

@sio.event
def disconnect():
	print("I'm disconnected!")
	exit()

@sio.event(namespace='/cmd_suricate')
def cmd_1(data):
	my_logger.info("+ Recieved cmd_1")
	camera.stop()


parser = argparse.ArgumentParser()
parser.add_argument("-host", help="host to connecto: http://host:port")
args = parser.parse_args()
if args.host:
	host = args.host
else:
	exit()


my_logger.info("Connecting to host: [%s]", host)

sio.connect(host, namespaces=['/video_stream', '/cmd_suricate'])

my_logger.info("Geting camera")

camera = Camera()
while True:
	my_logger.info("Frame")

	frame = camera.get_frame()
	sio.emit('frame', frame, '/video_stream')
	
