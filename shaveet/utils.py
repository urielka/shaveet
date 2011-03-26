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
      
      
class IPMiddleware(object):
  def __init__(self,app,ips):
    self.app = app
    self.ips = set(ips)
    
  def __call__(self,env,start_response):
    
    if env.get('REMOTE_ADDR') in self.ips or not self.ips:
      return self.app(env,start_response)
    else:
      start_response('404 Not Found',[('Content-Type', 'text/html')])
      return ['Nothing here buddy']