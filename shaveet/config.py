import os.path

PORT = 8082
MAX_MESSAGES_PER_CHANNEL = 10
COMET_TIMEOUT = 25#Seconds
MAX_IDLE_CLIENT = 10#Seconds
MIN_ALIVE_TIME = 60
MAX_CLIENTS_GC = 1000
MAX_CLIENTS_RECONNECT = 100000#Amount of clients to keep for reconnection
MAX_CLIENT_RECONNECT_IDLE = 300#Seconds
CLIENT_GC_INTERVAL = 10

IPS = ['127.0.0.1']
LOG_PATH = os.path.expanduser('~/shaveet.log')