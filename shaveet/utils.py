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


class Node(object):
  __slots__ = ['prev', 'next', 'me']
  def __init__(self, prev, me):
    self.prev = prev
    self.me = me
    self.next = None

class LRU:
  """
  Implementation of a length-limited O(1) LRU queue.
  Built for and used by PyPE:
  http://pype.sourceforge.net
  Copyright 2003 Josiah Carlson.
  """
  def __init__(self, count, pairs=[]):
    self.count = max(count, 1)
    self.d = {}
    self.first = None
    self.last = None
    for key, value in pairs:
      self[key] = value
  def __contains__(self, obj):
    return obj in self.d
  def __getitem__(self, obj):
    a = self.d[obj].me
    self[a[0]] = a[1]
    return a[1]
  def __setitem__(self, obj, val):
    if obj in self.d:
      del self[obj]
    nobj = Node(self.last, (obj, val))
    if self.first is None:
      self.first = nobj
    if self.last:
      self.last.next = nobj
    self.last = nobj
    self.d[obj] = nobj
    if len(self.d) > self.count:
      if self.first == self.last:
        self.first = None
        self.last = None
        return
      a = self.first
      a.next.prev = None
      self.first = a.next
      a.next = None
      del self.d[a.me[0]]
      del a
  def __delitem__(self, obj):
    nobj = self.d[obj]
    if nobj.prev:
      nobj.prev.next = nobj.next
    else:
      self.first = nobj.next
    if nobj.next:
      nobj.next.prev = nobj.prev
    else:
      self.last = nobj.prev
    del self.d[obj]
  def __iter__(self):
    cur = self.first
    while cur != None:
      cur2 = cur.next
      yield cur.me[1]
      cur = cur2
  def iteritems(self):
    cur = self.first
    while cur != None:
      cur2 = cur.next
      yield cur.me
      cur = cur2
  def iterkeys(self):
    return iter(self.d)
  def itervalues(self):
    for i,j in self.iteritems():
      yield j
  def keys(self):
    return self.d.keys()