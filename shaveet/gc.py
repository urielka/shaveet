#std
import logging
#3rd
from gevent import Greenlet,sleep
#shaveet
from shaveet.config import MAX_CLIENTS_GC,CLIENT_GC_INTERVAL
from shaveet.lookup import all_clients,discard_client

logger = logging.getLogger("shaveet.gc")

class ClientGC(Greenlet):
  """
  this greenthread collects the clients that are no longer active
  """
  def run(self):
    while True:
      logger.info("ClientGC:processing clients")
      client_processed = 0
      for client_id,client in all_clients().iteritems():
        if not client.is_active():
          logger.debug("ClientGC:collecting id:%s,ts:%d,waiting:%s",client.id,client.ts,client.is_waiting)
          discard_client(client)
        #process in chuncks of MAX_CLIENTS_GC,sleep(0) means yeild to next greenlet
        client_processed+=1
        if client_processed % MAX_CLIENTS_GC == 0:
            sleep(0)
      logger.info("ClientGC:sleeping")
      sleep(CLIENT_GC_INTERVAL)