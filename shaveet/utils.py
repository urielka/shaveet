from gevent.hub import getcurrent,get_hub
from uuid import uuid4

def guid():
  return str(uuid4()).replace("-","")

def maxfd():
    import resource
    return resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    
def setprocname(name):
  try:
    from setproctitle import setproctitle
    setproctitle(name)
  except:
    pass
  
def waitany(events):
  """
  wait until any of the provided events get triggered
  """
  switch = getcurrent().switch
  try:
    for ev in events:
      ev.rawlink(switch)
    return get_hub().switch()
  finally:
    for ev in events:
      ev.unlink(switch)