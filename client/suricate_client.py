import argparse
import logging
import logging.config
from os import name
from time import sleep
import socketio
from camera import Camera

stream_video = False
camera = None

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
def start_video_stream(data):
	global stream_video
	global camera
	my_logger.info("+ Recieved start_video_stream")
	
	my_logger.info("Geting camera... " + str(stream_video))
	camera = Camera()
	stream_video = True

@sio.event(namespace='/cmd_suricate')
def stop_video_stream(data):
	global stream_video
	global camera
	my_logger.info("+ Recieved stop_video_stream")
	
	my_logger.info("Stoping camera... " + str(stream_video))
	camera =None
	stream_video = False


parser = argparse.ArgumentParser()
parser.add_argument("-host", help="host to connecto: http://host:port")
args = parser.parse_args()
if args.host:
	host = args.host
else:
	exit()


my_logger.info("Connecting to host: [%s]", host)

sio.connect(host, namespaces=['/video_stream', '/cmd_suricate'])


while True:

	my_logger.info("Waiting... " + str(stream_video))
	sleep(1)
	if stream_video == True:
		my_logger.info("Frame")

		frame = camera.get_frame()
		sio.emit('frame', frame, '/video_stream')
	else:
		sleep(1)

