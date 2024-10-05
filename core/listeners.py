#/usr/bin/env python3
#Python3
import config.mqtt_conf as mqtt_config
import logging as logger
import paho.mqtt.client as mqtt

from core.launcher import Listener, Manager
import socket
import config.udp_conf as udp_conf
import config.tcp_conf as tcp_conf
import config.common_conf as settings
import config.rabbitmq_conf as rabbit_conf
import pika


log = logger.getLogger(__name__)

# MqttListener is a client mqtt used to subscribe on remote topic, and forward received message to Manager
class MqttListener(Listener):
    """ MqttListener is a client mqtt used to subscribe on remote topic, and forward received message to Manager
    """

    def __init__(self, mqtt_host=mqtt_config.MQTT_SERVER, mqtt_port = mqtt_config.MQTT_PORT, manager = Manager()) -> None:
        self.__mqtt_host = mqtt_host
        self.__mqtt_port = mqtt_port
        self.__mqtt_client = mqtt.Client(client_id=mqtt_config.DEFAULT_CLIENT_ID, clean_session=mqtt_config.CLEAN_SESSION, userdata=None)
        self.__init_auth()
        self.__manager = manager
        self.__mqtt_client.on_connect = self.__on_connect
        self.__mqtt_client.on_message = self.__on_message
        self.__mqtt_client.on_subscribe = self.__on_subscribe
        self.__topic_in = mqtt_config.TOPIC_PREFIX_KEY + mqtt_config.DEFAULT_TOPIC_IN
        self.__topic_out = mqtt_config.TOPIC_PREFIX_KEY + mqtt_config.DEFAULT_TOPIC_OUT

    def __init_auth(self) -> None:
        if mqtt_config.AUTH_ENABLED:
            # set username and password
            self.__mqtt_client.username_pw_set(mqtt_config.DEFAULT_BROKER_USER, mqtt_config.DEFAULT_BROKER_PASSWORD)

        if mqtt_config.TLS_ENABLED:
            # enable TLS for secure connection
            self.__mqtt_client.tls_set(tls_version=mqtt_config.TLS_VERSION)

    # The callback for when the client receives a CONNACK response from the server.
    def __on_connect(self, client, userdata, flags, rc):
        log.info("Connected with result code "+str(rc))
        
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.__mqtt_client.subscribe(self.__topic_in)

    # print which topic was subscribed to
    def __on_subscribe(client, userdata, mid, granted_qos, properties=None):
        log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    # The callback for when a PUBLISH message is received from the server.
    def __on_message(self, client, userdata, msg):
        message_str = str(msg.payload)
        log.info("message on topic " + msg.topic+": " + message_str)
        self.__manager.execute(message_str)
        self.__mqtt_client.publish(self.__topic_out, 'ACK ' + message_str)

    def run(self, mode=mqtt_config.DEFAULT_LOOP_MODE) -> None:
        self.__mqtt_client.connect(self.__mqtt_host, self.__mqtt_port, 60)

        self.__mqtt_client.enable_logger()

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        if mode== 'loop_forever':
            self.__mqtt_client.loop_forever()
        elif mode== 'loop_start':
            self.__mqtt_client.loop_start()

    def close(self):
        self.__manager.close()


# UdpListener is a server udp used to receive a message from remote client, and forward it to Manager
class UdpListener(Listener):
    """ UdpListener is a server udp used to receive a message from remote client, and forward it to Manager
    """
    def __init__(self, local_host = udp_conf.LOCAL_IP, local_port = udp_conf.LOCAL_PORT, manager = Manager()) -> None:
        super().__init__()
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__local_host = local_host
        self.__local_port = local_port
        self.manager = manager

    def run(self) -> None:
        self.__socket.bind((self.__local_host, self.__local_port))
        log.info('Started UDP server on (' + str(self.__local_host) + ', ' + str(self.__local_port) + ')')
        while True:
            bytes_address_pair = self.__socket.recvfrom(4096)
            message = bytes_address_pair[0].decode()
            address = bytes_address_pair[1]
            log.info("Message {} from client {}".format(message, address))
            self.manager.execute(message)

# TcpListener is a tcp server used to receive a message from remote client, and forward it to Manager
class TcpListener(Listener):
    """ TcpListener is a server tcp used to receive a message from remote client, and forward it to Manager
    """
    def __init__(self, local_host = tcp_conf.LOCAL_IP, local_port = tcp_conf.LOCAL_PORT, manager = Manager()) -> None:
        super().__init__()
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.__local_host = local_host
        self.__local_port = local_port
        self.manager = manager    

    def run(self) -> None:
        self.__socket.bind((self.__local_host, self.__local_port))
        log.info('Starting TCP server on (' + str(self.__local_host) + ', ' + str(self.__local_port) + ')')
        self.__socket.listen(1)
        while True:
            new_socket, address = self.__socket.accept()
            log.info("Incoming connection from {}".format(address))
            message = ''
            while True:
                received_bytes = new_socket.recv(4096)
                message = received_bytes.decode()
                log.info("Message {} from client {}".format(message, address))
                if not message or message.endswith('\r\n'): 
                    new_socket.close()
                    break
            self.manager.execute(message)

# RabbitMQListener is a server used to receive a message from rabbit queue, and forward it to Manager
class RabbitMQListener(Listener):
    """ RabbitMQListener is a server used to receive a message from rabbit queue, and forward it to Manager
    """
    def __init__(self, host = rabbit_conf.HOST, port = rabbit_conf.PORT, queue_cmd_in=rabbit_conf.CMD_QUEUE_IN) -> None:
        super().__init__()
        self.__host = host
        self.__port = port
        self.__queue_cmd_in = queue_cmd_in
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.__host), port=self.__port)
        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(queue=self.__queue_cmd_in)
    
    def __on_message_received(self, ch, method, properties, body):
        log.info("Message {} from queue {}".format(str(body), self.__queue_cmd_in))
        self.manager.execute(str(body).replace('\r', '').replace('\n'))        
        
    def run(self) -> None:
        self.__channel.basic_consume(queue=self.__queue_cmd_in, on_message_callback=self.__on_message_received, auto_ack=True)
        log.info(' Waiting for messages. To exit press CTRL+C')
        self.__channel.start_consuming()


# factory method for Listener instance
def init_listener() -> Listener:
    if settings.listener_enabled_flags['mqtt']:
        return MqttListener()
    elif settings.listener_enabled_flags['udp']:
        return UdpListener()
    elif settings.listener_enabled_flags['tcp']:
        return TcpListener()
    elif settings.listener_enabled_flags['rabbitmq']:
        return RabbitMQListener()
    else:
        return Listener()