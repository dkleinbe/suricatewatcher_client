import argparse
import logging
from os import name
import socketio
from camera import Camera


my_logger = logging.getLogger(__name__)
my_logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
my_logger.addHandler(ch)

my_logger.info("LAUNCHING APP")

sio = socketio.Client(logger=False, engineio_logger=False)


@sio.event
def connect():
	print("I'm connected!")
	my_logger.info("I'm connected!")
	

@sio.event
def connect_error(data):
	print("The connection failed!")
	exit()

@sio.event
def disconnect():
	print("I'm disconnected!")
	exit()

@sio.event(namespace='/cmd')
def cmd_1(data):
	print("+ Recieved cmd_1")
	my_logger.info("+ Recieved cmd_1")


parser = argparse.ArgumentParser()
parser.add_argument("-host", help="host to connecto: http://host:port")
args = parser.parse_args()
if args.host:
	host = args.host
else:
	exit()


#logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

my_logger.setLevel(logging.DEBUG)
my_logger.info("Connecting to host: [%s]", host)

sio.connect(host, namespaces=['/video_stream', '/cmd_suricate'])

camera = Camera()
while True:
	print("Frame")
	frame = camera.get_frame()
	sio.emit('frame', frame, '/video_stream')
	
