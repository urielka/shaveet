from flask import Flask,request
from wsgi_jsonrpc.json_tools import ServerProxy
from uuid import uuid4
from json import dumps

app = Flask(__name__)

@app.route("/create_client")
def create_client():
  shaveet = ServerProxy("http://localhost:8082")
  client_id = request.args.get('name') + "_" + str(uuid4()).replace("-","") + 'S3CR37';
  key = shaveet.create_client(client_id)['result']
  shaveet.subscribe(client_id,'chat-room')
  return dumps({'key':key,'client_id':client_id})

@app.route("/new_message")
def new_message():
  shaveet = ServerProxy("http://localhost:8082")
  shaveet.new_message(request.args.get('client_id'),request.args.get('msg'),'chat-room',False);
  return "1"

if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0')
