Shaveet comet server
-----------------------------------------------

Shaveet is a zero-config JSONP/CORS long-polling(AKA comet) server.

Why does it exist?
------------------

In [Binfire](http://www.binfire.com/ "a Online project management software") we needed a way to send realtime updates to connected clients.  
Looking around for solutions we encouter [hookbox](http://hookbox.org/ hookbox) which was almost what we needed but integrated with the application using webhooks and also was written in eventlet while all our infrastrcture is written with gevent.  
Shaveet was written in a way that allows minimal changes in the application code to integrate with it.


Installing
----------

Shaveet is avaliabe in PyPI,just run:
  sudo pip install shaveet

Running
-------
To run Shaveet in testing mode,run:

  shaveet

To run in daemon mode(for production use) run:

  shaveet -d


How do I use it?
----------------
