var Shaveet = {
  _listeners:{},
  _baseURL:null,
  client_ids:[],
  initiated:false,
  init:function(client_id,key)
  {
    Shaveet.client_ids.push(client_id+"|" + key);
    if(!Shaveet.initiated)
    {
      Shaveet.initiated = true;
      Shaveet.getBaseURL();
      Shaveet.Transports.CORS.init();
    }
    setTimeout(Shaveet.getEvents,1);
  },
  getBaseURL:function()
  {
    var scripts = document.getElementsByTagName("script");
    for(var i=0;i<scripts.length;i++)
      if(scripts[i].src.indexOf("/static/shaveet.js") != -1)
      {
        Shaveet._baseURL = scripts[i].src.replace("/static/shaveet.js","").replace(/\?.*$/,"");
        break;
      }
  },
  getEvents:function()
  {
    var ids = "";
    for(var i=0;i<Shaveet.client_ids.length;i++)
      ids += "&client_id=" + Shaveet.client_ids[i];
    var url = Shaveet._baseURL + '/message_updates?callback=?' + ids;
    if(Shaveet.Transports.CORS.provider)//has support for Cross Domain Requests
      Shaveet.Transports.CORS(url,Shaveet.onEvents,Shaveet.onError);
    else
      Shaveet.Transports.JSONP(url,Shaveet.onEvents,Shaveet.onError);
  },
  onEvents:function(channels)
  {
    for(var channelName in channels)
    {
      var listeners = Shaveet._listeners[channelName] ? Shaveet._listeners[channelName] : Shaveet._listeners["*"];
      if(listeners)
      {
        var updates = channels[channelName];    
        for(var j=0;j<updates.length;j++)
          updates[j] = {
            id:updates[j][0],
            client_id:updates[j][2],
            payload:Shaveet._safeEval(updates[j][1]),
            payload_raw:updates[j][1],
            channelName:channelName
          };
        for(var i=0;i<listeners.length;i++)
        {
            try{listeners[i](updates);}
            catch(e){}
        }	
      }
    }
    setTimeout(Shaveet.getEvents,1);
  },  
  onError:function()
  {
    //on error retry to reconnect to Comet service
    //TODO:on 404 status code(i.e. the comet client was GCed) show a alert and refresh the page
    setTimeout(Shaveet.getEvents,1000);
  },
  listenBulk:function(channel_name,func){
    if(!Shaveet._listeners[channel_name])
      Shaveet._listeners[channel_name] = [];
    Shaveet._listeners[channel_name].push(func);
  },
  listenSingle:function(channel_name,func)
  {
    return Shaveet.listenBulk(channel_name,function(updates)
    {
      for(var i=0;i<updates.length;i++)
        func(updates[i]);
    });
  },
  stopListening:function(channel_name)
  {
    delete Shaveet._listeners[channel_name];
  },
  _safeEval:function(str)
  {
    try{ return eval("(" + str + ")"); }
    catch(e) { return null; }
  }
};

var MutableSet = function(vals)
{
  this.length = 0;
  this._vals = {};
  if(vals && vals.length)
    for(var i=0;i<vals.length;i++)
      this.add(vals[i]);
};
MutableSet.prototype = {
  add:function(val)
  {
    this._vals[val] = true;
    this.length++;
  },
  remove:function(val)
  {
    if(this._vals[val])
    {
      delete this._vals[val];
      this.length--;
    }
  },
  contains:function(val)
  {
    return !!this._vals[val];
  },
  vals:function()
  {
    var ret = [];
    for(var val in this._vals)
      ret.push(val);
    return ret;
  }
};

Shaveet.Transports = {};

Shaveet.Transports.CORS = function (url,clbk,error){
  var request = new Shaveet.Transports.CORS.provider();
  url = url.replace("callback=?","callback=noop");
  request.open("get",url,true);
  request.onload = function(){
    clbk(eval(request.responseText.replace(/noop\(/,'(').replace(/\);$/,')')));
  }
  request.onerror = function(ev){
    if(error)error(request);
  }
  request.send();
};

Shaveet.Transports.CORS.init = function()
{
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr)
    Shaveet.Transports.CORS.provider = XMLHttpRequest;
  else if (typeof XDomainRequest != "undefined")
    Shaveet.Transports.CORS.provider = XDomainRequest;
  else
    Shaveet.Transports.CORS.provider = false;
};

Shaveet.Transports.JSONP = function(url,clbk,error){$.jsonp({url:url,success:clbk,error:error});};

