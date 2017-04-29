from datastore.db import GetDB

class Alerts:
    DANGER_LEVEL = "dangerLevel"
    DANGER_LEVEL_HOLD = "hold"
    DANGER_LEVEL_ESCAPE = "escape"
    DANGER_LEVEL_NODANGER = "nodanger"
    DANGER_LEVEL_0 = 0 # nodanger
    DANGER_LEVEL_1 = 1 # hold
    DANGER_LEVEL_2 = 2 # escape
    
    def PushAlert(clientID, dangerLevel):
        try:        
            GetDB().Alerts.insert_one({"clientID":clientID, Alerts.DANGER_LEVEL:dangerLevel})
        except Exception as e:
            print("Failed to connect client: %s, error: %s" % (clientID, e))  
        
    def EnumerateAlerts(callback):
        result = None
        try:
            alerts = GetDB().Alerts.find()
            for alert in alerts:
                clientID = alert["clientID"]
                dangerLevel = alert[Alerts.DANGER_LEVEL]
                if callback(clientID, dangerLevel):
                    # Delete processed alert
                    GetDB().Alerts.delete_one({"clientID":clientID})
        except Exception as e:
            print("Failed to enumerate alerts, error: %s" % e)        
        