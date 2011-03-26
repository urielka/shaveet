#std
from __future__ import with_statement
from os import sep,path
from optparse import OptionParser
import sys,logging,logging.handlers,traceback
#3rd party
from static import Cling
from daemon import DaemonContext
from gevent import wsgi
#fix path
sys.path.append(sep.join(path.dirname(path.abspath(__file__)).split(sep)[:-1]))
#shaveet
from shaveet import config,api,gc
from shaveet.utils import maxfd,setprocname

BASE_PATH = path.dirname(path.abspath(__file__))
logger_wsgi = logging.getLogger("wsgi_jsonrpc")
logger = logging.getLogger("shaveet.gc")
static_app = Cling(path.dirname(path.abspath(__file__)))

def wsgi_main(env, start_response):
  try:
    if env['PATH_INFO'] == '/':
      return api.handle(env,start_response)
    elif env['PATH_INFO'].startswith('/message_updates'):
      return [api.message_updates(env,start_response)]
    elif env['PATH_INFO'].startswith('/static'):
      return static_app(env, start_response)
    else:
      start_response('404 Not Found', [('Content-Type', 'text/plain')])
      return 'Not Found\r\n'
  except GeneratorExit:#Python 2.5 fix
    pass
  except Exception,e:
    start_response('500 Internal server error', [('Content-Type', 'text/plain')])
    logger.error(traceback.format_exc())
    return 'Internal server error\r\n'

def main(options):
  server = wsgi.WSGIServer(('', config.PORT), wsgi_main)
  client_gc = gc.ClientGC()
  try:
    client_gc.start()
    server.serve_forever()
  except KeyboardInterrupt:
    server.stop()

if __name__ == "__main__":
  setprocname("shaveet")
  parser = OptionParser()
  parser.add_option("-d", "--daemon", dest="daemon",help="ruan as daemon",action="store_true",default=False)
  (options, args) = parser.parse_args()
  
  formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
  #setup handlers
  fh = logging.handlers.RotatingFileHandler(config.LOG_PATH,maxBytes = 1024 * 1024,backupCount=3)
  ch = logging.StreamHandler()
  #set formmaters
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
  logger_wsgi.setLevel(logging.INFO)
  logger.setLevel(logging.INFO)

  if options.daemon:
    with DaemonContext(files_preserve=range(maxfd() + 2)):      
      logger.addHandler(fh)
      logger_wsgi.addHandler(fh)
      logger.info("starting daemon..")
      main(options)
  else:
    logger.setLevel(logging.DEBUG)
    logger_wsgi.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger_wsgi.addHandler(ch)
    main(options)
