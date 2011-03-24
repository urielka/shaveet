from time import time
from json import dumps
#gevent
from gevent.event import Event
from gevent import Timeout
#binfire
from shaveet.lookup import get_client,get_channel,channel_exist,client_exists
from shaveet.config import COMET_TIMEOUT
from shaveet.utils import waitany

MESSAGE_INDEX = 0
CLIENT_ID_INDEX = 1
ID_INDEX = 2

class ChannelCursor(object):
  """
  represent the position of a client in the channel(i.e. which messages he got up to this point
  """
  
  __slots__ = ('channel','cursor')
  
  def __init__(self,channel,cursor):
    self.channel = channel
    self.cursor = cursor
    
class Message(object):
  """
  represent a message in the channel.
  """
  
  __slots__ = ('client_id','message','id','system')
  
  def __init__(self,client_id,message,id,system):
    self.client_id = client_id
    self.message = message
    self.id = id
    self.system = system

class Channel(object):
  """
  Represent a channel in shaveet,a channel is something that clients can subscribe to and publish messages to.
  Each subscribed client get all the messages published to the channel.
  Each channel is identified by a name unique to that channel
  """
  
  __slots__ = ('clients','messages','new_message_event','max_messages','id','name')
  
  def __init__(self,name,max_messages):
    self.name = name
    #a cache of recent messages limited by max_messages
    self.messages = []
    #a event that fire on every new message
    self.new_message_event = Event()
    self.max_messages = max_messages
    self.id = 1
    self.clients = set()
    
  def add_client(self,client_id):
    self.clients.add(client_id)
    self.new_message(client_id,dumps({"type":"subscribe"}),True)
    
  def remove_client(self,client_id,gc=False):
    self.clients.discard(client_id)
    self.new_message(client_id,dumps({"type":"unsubscribe","gc":gc}),True)

  def new_message(self,client_id,message,system=False):
    self.messages.append(Message(client_id,message,self.id,system))
    self.id += 1
    #trim list,remove old messages
    if len(self.messages) > self.max_messages:
      self.messages = self.messages[-self.max_messages:]
    self.new_message_event.set()
    self.new_message_event.clear()

  def get_updates(self,cursor):
    """
    get updates for the channel,if there is no updates returns a event for notification
    """
    if not self.messages or cursor >= self.messages[-1].id:
      return self.new_message_event
    
    return [message for message in self.messages if message.id > cursor]
    
  def get_active_clients(self):
    now = int(time())#saves call to time
    return [client_id for client_id in self.clients
              if client_id and not "admin" in client_id and client_exists(client_id) and get_client(client_id).is_active(now)]
              
  def __hash__(self):
    return hash(self.name)
    

def get_updates(clients):
  """
  get all updates from the channels and waits until one channel have new information
  """
  #channel name -> messages
  updates = {}
  #events to wait for
  events = []
  #cursors for each channel
  cursors = []
  for client in clients:
    client.touch()
    for channel_name,cursor in client.channels.iteritems():
      if channel_exist(channel_name):
        cursors.append(ChannelCursor(get_channel(channel_name),cursor))
  #check for available messages
  for cc in cursors:
    update = cc.channel.get_updates(cc.cursor)
    if type(update) is Event:
      events.append(update)
    else:
      updates[cc.channel.name] = update
  #found messages,so just return them
  if len(updates) > 0:
    return updates
  #no messages,so wait for any event
  elif len(events) > 0:
    fired = False
    try:
      #mark the client as waiting so the GC doesn't collect them
      for client in clients:
        client.mark_waiting()
      #wait for any event to get fired up to COMET_TIMEOUT seconds
      with Timeout(COMET_TIMEOUT,False) as timeout:
        waitany(events + [client.channels_event for client in clients])
        fired = True
    finally:
      #clear the marking
      for client in clients:
        client.touch()
        client.clear_waiting()
    if fired:
      return get_updates(clients)
    else:#timeout
      return {}
  #no channels
  else:
    return {}