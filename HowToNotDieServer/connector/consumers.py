from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
#from channels.security.websockets import allowed_hosts_only
import json

from datastore.clients import ActiveClients
from processor.main import Processor
 
# Connected to websocket.connect
def ws_connect(message):
    global client_id, data
    # Accept the connection
    message.reply_channel.send({"accept": True})
    
    clientID = str(message.reply_channel)
    ActiveClients.Connect(clientID, message.reply_channel)

# Connected to websocket.receive
def ws_message(message):
    try:
        inputData = json.loads(message.content['text'])
        clientID = str(message.reply_channel)
        outputData = Processor.ProcessClientMessage(clientID, inputData)
        outputDataStr = ''
        if outputData:
            dataToDump = {"result":"success", "type":"response", "data":outputData}
            outputDataStr = json.dumps(dataToDump)
        else:
            outputDataStr = "{\"result\":\"failure\"}"
        message.reply_channel.send({'text':outputDataStr})
    except Exception as e:
        print("Failed to process the message, error: %s" % (e))
        message.reply_channel.send({'text':"{\"result\":\"failure\"}"})

# Connected to websocket.disconnect
def ws_disconnect(message):
    clientID = str(message.reply_channel)
    ActiveClients.Disconnect(clientID)
    
