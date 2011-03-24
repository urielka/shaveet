var CometBus = {
  _listeners:{},
  _baseURL:null,
  client_ids:[],
  initiated:false,
  init:function(client_id)
  {
    CometBus.client_ids.push(client_id);
    if(!CometBus.initiated)
    {
      CometBus.initiated = true;
      CometBus.getBaseURL();
      CometBus.Transports.CORS.init();
    }
    setTimeout(CometBus.getEvents,1);
  },
  getBaseURL:function()
  {
    var scripts = document.getElementsByTagName("script");
    for(var i=0;i<scripts.length;i++)
      if(scripts[i].src.indexOf("/static/cometbus.js") != -1)
      {
        CometBus._baseURL = scripts[i].src.replace("/static/cometbus.js","").replace(/\?.*$/,"");
        break;
      }
  },
  getEvents:function()
  {
    var ids = "";
    for(var i=0;i<CometBus.client_ids.length;i++)
      ids += "&client_id=" + CometBus.client_ids[i];
    var url = CometBus._baseURL + '/message_updates?callback=?' + ids;
    if(CometBus.Transports.CORS.provider)//has support for Cross Domain Requests
      CometBus.Transports.CORS(url,CometBus.onEvents,CometBus.onError);
    else
      CometBus.Transports.JSONP(url,CometBus.onEvents,CometBus.onError);
  },
  onEvents:function(channels)
  {
    for(var channelName in channels)
    {
      var listeners = CometBus._listeners[channelName] ? CometBus._listeners[channelName] : CometBus._listeners["*"];
      if(listeners)
      {
        var updates = channels[channelName];    
        for(var j=0;j<updates.length;j++)
          updates[j] = {
            id:updates[j][0],
            client_id:updates[j][2],
            payload:CometBus._safeEval(updates[j][1]),
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
    setTimeout(CometBus.getEvents,1);
  },  
  onError:function()
  {
    //on error retry to reconnect to Comet service
    //TODO:on 404 status code(i.e. the comet client was GCed) show a alert and refresh the page
    setTimeout(CometBus.getEvents,1000);
  },
  listenBulk:function(channel_name,func){
    if(!CometBus._listeners[channel_name])
      CometBus._listeners[channel_name] = [];
    CometBus._listeners[channel_name].push(func);
  },
  listenSingle:function(channel_name,func)
  {
    return CometBus.listenBulk(channel_name,function(updates)
    {
      for(var i=0;i<updates.length;i++)
        func(updates[i]);
    });
  },
  stopListening:function(channel_name)
  {
    delete CometBus._listeners[channel_name];
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

CometBus.Transports = {};

CometBus.Transports.CORS = function (url,clbk,error){
  var request = new CometBus.Transports.CORS.provider();
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

CometBus.Transports.CORS.init = function()
{
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr)
    CometBus.Transports.CORS.provider = XMLHttpRequest;
  else if (typeof XDomainRequest != "undefined")
    CometBus.Transports.CORS.provider = XDomainRequest;
  else
    CometBus.Transports.CORS.provider = false;
};

CometBus.Transports.JSONP = function(url,clbk,error){$.jsonp({url:url,success:clbk,error:error});};

