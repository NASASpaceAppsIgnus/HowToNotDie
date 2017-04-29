from datastore.clients import ActiveClients
from datastore.areas import Areas
from datastore.alerts import Alerts

class Processor:
    COMMANDS = {"geo":0, "aware":1,"escaping":2} # command -> client state
    def ProcessClientMessage(clientID, inputData):
        clientState = 0
        try:
            command = inputData["command"]
            if command == "pushAlert":
                position = [30, 40]
                ActiveClients.UpdateClient(clientID, "$set", {ActiveClients.POSITION:position, ActiveClients.CLIENT_STATE:clientState})                
                Alerts.PushAlert(clientID, Alerts.DANGER_LEVEL_ESCAPE)
                return {Alerts.DANGER_LEVEL:Alerts.DANGER_LEVEL_ESCAPE}
            clientState = COMMANDS[command]
            lat = float(inputData["lat"])
            lng = float(inputData["lng"])
        except Exception as e:
            print("Failed to process client %s message: %s, error: %s" % (clientID, inputData, e)) 
            return None
        position = [lat, lng]
        ActiveClients.UpdateClient(clientID, "$set", {ActiveClients.POSITION:position, ActiveClients.CLIENT_STATE:clientState})
        #TODO save danger level inside client record
        outputData = {Alerts.DANGER_LEVEL:Alerts.DANGER_LEVEL_NODANGER}
        Areas.Load(client[ActiveClients.POSITION], outputData)
        return outputData
        
    def EnumAlertsCallback(clientID, dangerLevel):
        client = ActiveClients.FindClient(clientID)
        if client and ActiveClients.POSITION in client:
            outputData = {Alerts.DANGER_LEVEL:dangerLevel}
            Areas.Load(client[ActiveClients.POSITION], outputData)
            ActiveClients.Respond(clientID, outputData)
            return True

    def PeriodicProcess():
        Alerts.EnumerateAlerts(Processor.EnumAlertsCallback)