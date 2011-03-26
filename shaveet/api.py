# -*- coding: utf-8 -*-
#std
from datetime import datetime
from urllib import unquote
from urlparse import parse_qs
try:
  from json import loads,dumps
except ImportError:#Python 2.5
  from simplejson import loads,dumps
#3rd
import wsgi_jsonrpc
#binfire
from shaveet.utils import IPMiddleware
from shaveet.config import COMET_TIMEOUT,IPS
from shaveet.lookup import get_client,get_client_with_key,get_channel,channel_exist,discard_client,create_client
from shaveet.channel import get_updates

def message_updates(env,start_response):
  """
  handles clients long polling,wait for updates and return them or timeout
  """
  #parse request,looks like ?client_id=....&client_id=....&callback=...
  qs = parse_qs(env['QUERY_STRING'])
  #client_id is client_id;key
  client_ids = qs["client_id"]
  callback = qs["callback"][0]
  try:
    cursors = []
    clients = [get_client_with_key(client_id_key) for client_id_key in client_ids]
    #get the updates,blocks if no updates found
    updates = get_updates(clients)
    #if updates found update the clients cursors
    for client in clients:
      client.update_cursors(updates)
    start_response('200 OK', [('Content-Type', 'application/x-javascript'),('Access-Control-Allow-Origin','*')])
    #generates the response like: callback({"channel_1":[[message],[message]],"channel_2":[[message]]})
    return "".join([callback,"(",dumps(dict((channel_name,[[message.id,message.message,message.client_id] for message in messages]) 
                                                                                  for channel_name,messages in updates.iteritems())),");"])
  except KeyError:#one of the clients doesn't exists
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return "Not Found\r\n"  


def subscribe(client_id,channel_name):
  """
  subscribe the client to the channel
  
  client_id - id of the client
  channel_name - name of the channel
  """
  get_client(client_id).add_channel(channel_name)
  return 1

def unsubscribe(client_id,channel_name):
  """
  unsubscribe the client to the channel
  
  client_id - id of the client
  channel_name - name of the channel
  """
  get_client(client_id).remove_channel(channel_name)
  return 1
  
def subscribe_many(channels):
  """
  subscribe many clients to many channels
  
  channels - a dict like this {
    channel_name:[client_id,client_id2]
  }
  """
  for channel,clients in channels.iteritems():
    for client_id in clients:
      subscribe(client_id,channel)

def unsubscribe_many(channels):
  """
  unsubscribe many clients to many channels
  
  channels - a dict like this {
    channel_name:[client_id,client_id2]
  }
  """
  for channel,clients in channels.iteritems():
    for client_id in clients:
      unsubscribe(client_id,channel)
      
def unsubscribe_all_channel(channel_name,exclude):
  """
  unsubscribe all the clients from the channel except those in the exclude list
  
  channel_name - name of the channel
  exclude - a list of clients to exclude from this operation
  """
  unsubscribe_many({channel_name:filter(lambda x: not x in exclude,get_channel_clients(channel_name))})

def new_message(client_id,message,channel_name,system):
  """
  publish a new message into the channel message queue
  
  client_id - the publishing client id
  message - a string or object to publish,if it is a object it is sent as a json string
  channel_name - the name of the channel to publish this message
  system - true for system messages(like unsubscribe because of GC)
  """
  if not (type(message) is str or type(message) is unicode):
    message = dumps(message)
  get_channel(channel_name).new_message(client_id,message,system)
  return 1
  
def get_channel_clients(channel_name):
  """
  get all the clients subscribed to the channel
  
  channel_name - name of the channel
  """
  
  return get_channel(channel_name).get_active_clients()
  
def get_client_channels(client_id):
  """
  get all the clients subscribed to the channel
  
  channel_name - name of the channel
  """
  
  return get_client(client_id).get_subscribed_channels()
  
def kill_client(client_id):
  return discard_client(get_client(client_id))
  
#this is the wsgi application entry point
api_wsgi = wsgi_jsonrpc.WSGIJSONRPCApplication(methods=[subscribe,subscribe_many,unsubscribe,unsubscribe_many,unsubscribe_all_channel,new_message,
                                                        get_channel_clients,get_client_channels,kill_client,create_client])
                                                        
handle = IPMiddleware(api_wsgi,IPS)

