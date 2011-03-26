#std
from time import time
#gevent
from gevent.event import Event
#shaveet
from shaveet.utils import guid
from shaveet.consts import SYSTEM_ID,ADMIN_CHANNEL
from shaveet.config import MAX_MESSAGES_PER_CHANNEL,MAX_IDLE_CLIENT,COMET_TIMEOUT,MIN_ALIVE_TIME
import shaveet#for api

class Client(object):
  """
  Represents a client in shaveet,a client is identified by string called id and is unique per client.
  """
  __slots__ = ('id','channels','ts','create_ts','channels_event','is_waiting','key')

  def __init__(self,id):
    self.id = id
    self.channels = {}
    #timestamp of last action,used for GC
    self.ts = int(time())
    #when this object was created
    self.create_ts = int(time())
    self.channels_event = Event()
    self.is_waiting = False
    self.key = guid()

  def touch(self):
    self.ts = int(time())
    
  def get_subscribed_channels(self):
    return self.channels.keys()
    
  def add_channel(self,channel_name):
    chn = get_channel(channel_name) 
    if not channel_name in self.channels:
      #set to chn.id so we don't get old messages
      self.channels[channel_name] = chn.id - 1  
    chn.add_client(self.id)
    #notifies that this client has a new channel
    self.channels_event.set()
    self.channels_event.clear()

  def remove_channel(self,channel_name,gc=False):
    if channel_name in self.channels:
      del self.channels[channel_name]
    get_channel(channel_name).remove_client(self.id,gc)
    
  def update_cursors(self,updates):
    for channel_name,messages in updates.iteritems():
      if channel_name in self.channels:
        self.channels[channel_name] = messages[-1].id
    
  def mark_waiting(self):
    self.is_waiting = True
    
  def clear_waiting(self):  
    self.is_waiting = False
    
  def is_active(self,now=False):
    #if now is provided use that to save a call to time
    if not now:
      now = int(time())
    idle_time = now - self.ts 
    alive_time = now - self.create_ts
    #if the client is idle for short period or waiting it is consider active
    return alive_time <= MIN_ALIVE_TIME or idle_time <= MAX_IDLE_CLIENT or (self.is_waiting and idle_time <= (10 + COMET_TIMEOUT))
    
  def remove_from_channels(self):
    for channel_name in self.channels.keys():
      self.remove_channel(channel_name,True)

#channel name -> Channel
_channels = {}
#client id -> Client
_clients = {}

###############
#  client     #
###############

def create_client(client_id):
  global _clients
  if not client_id in _clients:
    _clients[client_id] = Client(client_id)
  return _clients[client_id].key
  
def get_client(client_id):
  global _clients
  return _clients[client_id]  
  
def client_exists(client_id):
  global _clients
  return client_id in _clients
  
def all_clients():
  return _clients.copy()
  
def discard_client(client):
  if client_exists(client.id):
    client.remove_from_channels()
    del _clients[client.id]
    del client
    
def get_client_with_key(client_id_key):
  print client_id_key
  client_id,key = client_id_key.split("|")
  client = _clients[client_id]
  if client.key != key:
    raise KeyError("Wrong key for client")
  return client
###############
#  channel    #
###############
def get_channel(channel_name):
  from shaveet.channel import Channel
  global _channels
  if not channel_name in _channels:
    _channels[channel_name] = Channel(channel_name,MAX_MESSAGES_PER_CHANNEL) 
    shaveet.api.new_message(SYSTEM_ID,{"type":"new_channel","name":channel_name},ADMIN_CHANNEL,True)
  return _channels[channel_name]
  
def channel_exist(channel_name):
  global _channels
  return channel_name in _channels
    
