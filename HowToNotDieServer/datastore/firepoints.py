from datastore.db import GetDB
import urllib


class FirePoints:
    CONFIDENCE_THRESGHOLD = 80
    def Load():
        try:   
            url = "https://firms.modaps.eosdis.nasa.gov/active_fire/c6/text/MODIS_C6_Australia_and_New_Zealand_24h.csv"
            dataSource = urllib.request.urlopen(url)
            lines = dataSource.read()
            lines = lines.decode('utf-8')
            firstLine = True
            linesCounter = 0
            linesLoaded = 0
            GetDB().FirePoints.delete_many({})
            GetDB().Areas.delete_many({})
            GetDB().Cells.delete_many({})
            for line in lines.split('\n'):
                linesCounter = linesCounter + 1
                if firstLine:
                    firstLine = False
                    continue
                #latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp,daynight
                firePoint = {}
                try:
                    params = line.split(',')
                    latStr = params[0]
                    lngStr = params[1]
                    point = (float(latStr), float(lngStr))
                    dateStr = params[5]
                    timeStr = params[6]
                    confidence = int(params[8])
                    if confidence > FirePoints.CONFIDENCE_THRESGHOLD:
                        firePoint["point"] = point
                        firePoint["timeStamp"] = dateStr + " " + timeStr
                        FirePoints.GetWeatherData(firePoint)
                        FirePoints.InsertFirePoint(firePoint)
                        linesLoaded = linesLoaded + 1
                except:
                    continue
        except Exception as e:
            print("Failed to load firepoint %s, error: %s" % (line, e))
        print("Loaded %d out of %d fire points" % (linesLoaded, linesCounter))
     
    def GetWeatherData(firePoint):
        #hardcoded params for demo
        firePoint["windSpeed"] = 15
        firePoint["windDir"] = 2
        firePoint["temp"] = 30
        firePoint["humidity"] = 0.4 
        
    def InsertFirePoint(firePoint):
        try:        
            GetDB().FirePoints.insert_one(firePoint)
        except Exception as e:
            print("Failed to insert firepoint, error: %s" % (e))  
     
    def GetPoints():
        result = []
        try:
            firepoints = GetDB().FirePoints.find()
            for firepoint in firepoints:
                result.append(firepoint)
        except Exception as e:
            print("Failed to enumerate fire points, error: %s" % e)
        return result        
