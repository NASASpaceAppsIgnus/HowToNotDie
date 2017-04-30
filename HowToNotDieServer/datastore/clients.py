import json
from datastore.db import GetDB

class ActiveClients:
    POSITION = "position"
    CLIENT_STATE = "clentState"
    CLIENT_STATE_0 = 0 # unaware
    CLIENT_STATE_1 = 1 # aware
    CLIENT_STATE_2 = 2 # escaping 
    
    _responseChannels = {}
    
    def Connect(clientID, reply_channel):
        try:        
            GetDB().ActiveClients.insert_one({"clientID":clientID, "notified":0})
            ActiveClients._responseChannels[clientID] = reply_channel
        except Exception as e:
            print("Failed to connect client: %s, error: %s" % (clientID, e))            

    def Disconnect(clientID):
        try:
            GetDB().ActiveClients.delete_one({"clientID":clientID})
            ActiveClients._responseChannels[clientID] = None
        except Exception as e:
            print("Failed to diconnect client: %s, error: %s" % (clientID, e))
        
    def Respond(clientID, outputData):
        try:
            dataToDump = {"result":"sucess", "type":"alert", "data":outputData}
            outputStr = json.dumps(dataToDump)            
            channel = ActiveClients._responseChannels[clientID]
            channel.send({'text':outputStr})
        except Exception as e:
            print("Failed to respond client: %s, error: %s" % (clientID, e))
     
    def FindClient(clientID):
        result = None
        try:
            result = GetDB().ActiveClients.find_one({"clientID":clientID})
        except:
            pass
        return result
    
    def UpdateClient(clientID, operator, data):
        try:
            clientFilter = {"clientID":clientID} 
            GetDB().ActiveClients.update_one(clientFilter, {operator:data})
        except Exception as e:
            print("Failed to update client: %s, error: %s" % (clientID, e))        
            
    def EnumerateClients(callback):
        result = None
        try:
            clients = GetDB().ActiveClients.find()
            for client in clients:
                callback(client)
        except Exception as e:
            print("Failed to enumerate clients, error: %s" % e)
            
    def GetNumberOfClients():
        result = None
        try:
            clients = GetDB().ActiveClients.find()
            result = len(clients)
        except:
            print("Failed to calculate clients, error: %s" % e)
        return result
    
    def RemoveAll():
        GetDB().ActiveClients.delete_many({})
        ActiveClients._responseChannels = {}
