import paho.mqtt.client as mqtt
import paho
import socket

# mqtt parameters
MQTT_SERVER = 'SOMETHING.s1.eu.hivemq.cloud'
MQTT_PORT = 8883

# Enable authentication
AUTH_ENABLED = True
DEFAULT_BROKER_USER = 'mqtt-user'
DEFAULT_BROKER_PASSWORD = 'mypassword'

# TLS options for MQTT
TLS_ENABLED = True
TLS_VERSION = mqtt.ssl.PROTOCOL_TLS


# topic secret key (message prefix for unique topic)
TOPIC_PREFIX_KEY=''

# topic secret key (topic prefix for unique topic)
DEFAULT_TOPIC_IN = '/cmd/in'
DEFAULT_TOPIC_OUT = '/cmd/out'

CLEAN_SESSION=True

DEFAULT_CLIENT_ID=socket.gethostname() # get local hostname as clientID 

# it can be 'loop_forever' for loop_forever() or 'loop_start' for start_mode()
DEFAULT_LOOP_MODE = 'loop_forever'
