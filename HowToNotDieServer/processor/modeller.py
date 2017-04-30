from datastore.clients import ActiveClients
from datastore.areas import Areas
from datastore.alerts import Alerts
from datetime import datetime
from datastore.firepoints import FirePoints
from processor.calc import fire_constructor

class Modeller:
    def EnumClientsCallback(client):
        try:
            if client and ActiveClients.POSITION in client:
                data = {}
                position = client[ActiveClients.POSITION]
                Areas.Load(position, data)
                dangerLevel = Alerts.DANGER_LEVEL_NODANGER
                maxRisk = -1
                for areaToAvoid in data[Areas.AREA_TO_AVOID]:
                    if Areas.IsPointInBoundary(position, areaToAvoid["boundary"]):
                        risk = areaToAvoid["risk"]
                        if risk> maxRisk:
                            maxRisk = risk
                if maxRisk > 1:
                    dangerLevel = Alerts.DANGER_LEVEL_HOLD
                else:
                    dangerLevel = Alerts.DANGER_LEVEL_ESCAPE
                if client["notified"] != dangerLevel:
                    clientID = client["clientID"]
                    Alerts.PushAlert(clientID, dangerLevel)
                    ActiveClients.UpdateClient(clientID, "$set", {"notified":dangerLevel})
        except Exception as e:
            print("Failed to EnumClientsCallback: %s, error: %s" % (client, e))
                
    def RemoveAreaToAvoidCallback(area):
        if area["type"] == Areas.AREA_TO_AVOID:
            Areas.RemoveAreaToAvoid(area["data"]["boundary"])

    def PeriodicProcess():
        print("Start modeller")
        try:
            # Check clients in danger
            ActiveClients.EnumerateClients(Modeller.EnumClientsCallback)
            
            # Area modelling
            areasToRemove = Areas.GetAreas()
            newRev = Areas.GetDataRev() + 1
            
            firePoints = FirePoints.GetPoints()
            for firePoint in firePoints:
                 for risk in range(0,3):
                    # Fire prediction
                    boundaries = []
                    _, firePoints = Modeller.CalculateRiskZone(firePoint, risk)
                    Areas.AddDisplayPoly(firePoints, risk, newRev, "fire")
                    # Calc area to avoid
                    #boundary = Modeller.CalculateAreaToAvoid(firePoints)
                    #Areas.AddAreaToAvoid(boundary, risk, newRev)

            # Start using new dataset
            Areas.IncDataRev()
            # Remove old areas
            for area in Areas.GetAreas():
                if area["type"] == Areas.AREA_TO_AVOID:
                    Areas.RemoveAreaToAvoid(area["data"]["boundary"])
                elif area["type"] == Areas.DISPLAY_POLY: 
                    Areas.RemoveDisplayPoly(area["data"]["points"])
        except Exception as e:
            print("Failed to PeriodicProcess, error: %s" % (e)) 
        print("Done modeller")
                
    def CalculateRiskZone(firePoint, risk):
        avoidPoints = []
        firePoints = []
        try:
            firePosition = firePoint["point"]
            windSpeed = firePoint["windSpeed"]
            windDir = firePoint["windDir"]
            temp = firePoint["temp"]
            humidity = firePoint["humidity"]
            dateStr = firePoint["timeStamp"]
            timeSince = datetime.utcnow() - datetime.strptime(dateStr, "%Y-%m-%d %H%M")
            timeSinceHours = timeSince.total_seconds()/3600.0
            # Predict 0-4-8 hours
            timeSinceHours = timeSinceHours + (2 - risk) * 4
            avoidPoints, firePoints = fire_constructor(timeSinceHours,firePosition[0],firePosition[1],windSpeed)
            #print(timeSinceHours, dateStr)
        except Exception as e:
            print("Failed to CalculateRiskZone: %s, error: %s" % (firePoint, e))
        #TODO call fire prediction function
        return avoidPoints, firePoints
        
    def CalculateAreaToAvoid(points):
        return Areas.GetBoundary(points)
            