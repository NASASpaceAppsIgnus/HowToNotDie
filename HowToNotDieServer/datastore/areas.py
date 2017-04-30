from datastore.db import GetDB

class Areas:
    AREA_TO_AVOID = "areaToAvoid"
    SAFE_ZONES = "safeZones"
    DISPLAY_POLY = "displayPoly"
    DEFAULT_POSITION_RANGE_IN_DEG = 0.05
    
    PREDEFINED_SAFE_ZONES=((30, 30), (40, 40), (50, 50))
    """
        Data structure:
            CellID - encoded based on lat/long (e.g. lat -3.0, long 100.2 -> cellID = "0601002"
            Cell = {"cellID":cellID, "areas":[areaID1, areaID2...]
    """
    def UpdateCells(boundary, areaID, add = True):
        try: 
            cellIDs = Areas.GetCellIDsWithBoundary(boundary)
            for cellID in cellIDs:
                cell = GetDB().Cells.find_one({"cellID":cellID})
                if cell:
                    update = False
                    if add:
                        if areaID not in cell["areas"]:
                            cell["areas"].append(areaID)
                            update = True
                    else:
                        if areaID in cell["areas"]:
                            cell["areas"].remove(areaID)
                            if len(cell) == 0:
                                GetDB().Cells.delete_one({"cellID":cellID})
                            else:
                                update = True
                    if update:
                        GetDB().Cells.update_one({"cellID":cellID}, {"$set":{"areas":cell["areas"]}})
                elif add:
                    GetDB().Cells.insert_one({"cellID":cellID, "areas":[areaID]})

        except Exception as e:
            print("Failed to update cells: %s, error: %s" % (boundary, e))
            
    def GetDataRev():
        config = GetDB().Configs.find_one({"config":"areas"})
        if config:
            return config["updateRev"]
        GetDB().Configs.insert_one({"config":"areas","updateRev":0})
        return 0
    
    def IncDataRev():
        GetDB().Configs.update_one({"config":"areas"},{"$inc":{"updateRev":1}})        
    
    def AddAreaToAvoid(boundary, risk, dataRev):
        leftTopPoint = [boundary[0], boundary[1]]
        rightBottomPoint = [boundary[2], boundary[3]]         
        cellsMin = Areas.GetCellIDs(leftTopPoint, 0)
        cellsMax = Areas.GetCellIDs(rightBottomPoint, 0)
        areaID = "ATA" + cellsMin[0] + cellsMax[0]
        boundary = [leftTopPoint[0], leftTopPoint[1], rightBottomPoint[0], rightBottomPoint[1]]
        try:
            GetDB().Areas.delete_one({"areaID":areaID})
        except:
            pass
            
        try: 
            GetDB().Areas.insert_one({"areaID":areaID, "type":Areas.AREA_TO_AVOID, "rev":dataRev, "data":{"boundary":boundary,"risk":risk}})
            Areas.UpdateCells(boundary, areaID, add = True)

        except Exception as e:
            print("Failed to add area to avoid: %s, error: %s" % (boundary, e)) 
      
    def RemoveAreaToAvoid(boundary):
        leftTopPoint = [boundary[0], boundary[1]]
        rightBottomPoint = [boundary[2], boundary[3]]        
        cellsMin = Areas.GetCellIDs(leftTopPoint, 0)
        cellsMax = Areas.GetCellIDs(rightBottomPoint, 0)
        areaID = "ATA" + cellsMin[0] + cellsMax[0]
        boundary = [leftTopPoint[0], leftTopPoint[1], rightBottomPoint[0], rightBottomPoint[1]]
        try:
            GetDB().Areas.delete_one({"areaID":areaID})
            Areas.UpdateCells(boundary, areaID, add = False)
        except Exception as e:
            print("Failed to remove area to avoid: %s, error: %s" % (boundary, e)) 
            
    def RemoveDisplayPoly(points):
        boundary = Areas.GetBoundary(points)
        leftTopPoint = [boundary[0], boundary[1]]
        rightBottomPoint = [boundary[2], boundary[3]]          
        cellsMin = Areas.GetCellIDs(leftTopPoint, 0)
        cellsMax = Areas.GetCellIDs(rightBottomPoint, 0)
        areaID = "ATA" + cellsMin[0] + cellsMax[0]
        boundary = [leftTopPoint[0], leftTopPoint[1], rightBottomPoint[0], rightBottomPoint[1]]
        try:
            GetDB().Areas.delete_one({"areaID":areaID})
            Areas.UpdateCells(boundary, areaID, add = False)
        except Exception as e:
            print("Failed to remove area to avoid: %s, error: %s" % (boundary, e))            
        
    def AddDisplayPoly(points, risk, dataRev, type):
        boundary = Areas.GetBoundary(points)
        leftTopPoint = [boundary[0], boundary[1]]
        rightBottomPoint = [boundary[2], boundary[3]]          
        cellsMin = Areas.GetCellIDs(leftTopPoint, 0)
        cellsMax = Areas.GetCellIDs(leftTopPoint, 0)
        areaID = "DP" + cellsMin[0] + cellsMax[0]
        boundary = [leftTopPoint[0], leftTopPoint[1], rightBottomPoint[0], rightBottomPoint[1]]
        try:
            GetDB().Areas.delete_one({"areaID":areaID})
        except:
            pass
        
        try: 
            GetDB().Areas.insert_one({"areaID":areaID, "type":Areas.DISPLAY_POLY, "data":{"points":points,"risk":risk,"type":type}})
            Areas.UpdateCells(boundary, areaID, add = True)

        except Exception as e:
            print("Failed to add display poly: %s, error: %s" % (boundary, e))     
    
    def Load(position, data):
        data[Areas.AREA_TO_AVOID]=[]
        data[Areas.SAFE_ZONES]=[]
        data[Areas.DISPLAY_POLY]=[]
        
        for safeZone in Areas.PREDEFINED_SAFE_ZONES:
            data[Areas.SAFE_ZONES].append({"radius":Areas.DEFAULT_POSITION_RANGE_IN_DEG, "point":[safeZone[0], safeZone[1]]})
        
        try: 
            cellIDs = Areas.GetCellIDs(position, Areas.DEFAULT_POSITION_RANGE_IN_DEG)
            for cellID in cellIDs:
                cell = GetDB().Cells.find_one({"cellID":cellID})
                print(cell)
                if cell:
                    for areaID in cell["areas"]:
                        area = GetDB().Areas.find_one({"areaID":areaID})
                        if area:
                            areaType = area["type"]
                            if areaType == Areas.DISPLAY_POLY:
                                if area["data"] not in data[areaType]:
                                    data[areaType].append(area["data"])
                                    data[Areas.AREA_TO_AVOID].append({"boundary":Areas.CalculateAreaToAvoid(area["data"]["points"]), "risk":area["data"]["risk"]})

        except Exception as e:
            print("Failed to Load areas: %s, error: %s" % (position, e))
            
    def GetAreas():
        result = []
        try:
            areas = GetDB().Areas.find()
            for area in areas:
                result.append(area)
        except Exception as e:
            print("Failed to enumerate areas, error: %s" % e)
        return result
            
    def GetBoundary(points):
        if len(points) == 0:
            return None
        minLat = 90
        minLng = 180
        maxLat = -90
        maxLng = -180
        for point in points:
            if point[0] < minLat:
                minLat = point[0]
            if point[1] < minLng:
                minLng = point[1]
            if point[0] > maxLat:
                maxLat = point[0]
            if point[1] > maxLng:
                maxLng = point[1]
        return [minLat, minLng, maxLat, maxLng]
    
    def IsPointInBoundary(point, boundary):
        leftTopPoint = [boundary[0], boundary[1]]
        rightBottomPoint = [boundary[2], boundary[3]]
        if point[0] > leftTopPoint[0] and point[0] < rightBottomPoint[0] and point[1] > leftTopPoint[1] and point[1] < rightBottomPoint[1]:
            return True
        return False
            
    def GetCell(position):
        result = None
        try: 
            cellIDs = Areas.GetCellIDs(position, 0)
            for cellID in cellIDs:
                result = GetDB().Cells.find_one({"cellID":cellID})
                break
            
        except Exception as e:
            print("Failed to get cell areas: %s, error: %s" % (position, e))  
        return result
    
    def NormLat(lat):
        return int((lat + 90) * 10)
        
    def NormLng(lng):
        return int((lng + 180) * 10)
            
    def GetCellIDs(position, range):
        try: 
            lat = position[0]
            lng = position[1]
            #boundary box
            latMin = lat - range
            lngMin = lng - range
            latMax = lat + range
            lngMax = lng + range
            boundary = [latMin, lngMin, latMax, lngMax]
            return Areas.GetCellIDsWithBoundary(boundary)
        except Exception as e:
            print("Failed to GetCellIDs: %s, error: %s" % (position, e))  
        return []
    
    def GetCellIDsWithBoundary(boundary):
        result = []
        nlatMin = Areas.NormLat(boundary[0])
        nlngMin = Areas.NormLng(boundary[1])
        nlatMax = Areas.NormLat(boundary[2])
        nlngMax = Areas.NormLng(boundary[3])
    
        for i in range(nlatMin, nlatMax + 1):
            for j in range(nlngMin, nlngMax + 1):
                latStr = str(i)
                lngStr = str(j)
                if len(latStr) < 3:
                    latStr = 0*(3 - len(latStr)) + latStr
                if len(lngStr) < 4:
                    lngStr = 0*(4 - len(lngStr)) + lngStr                    
                result.append(latStr + lngStr)
        #print ("cells %d, %d, %d, %d, %d, %s" % (len(result), nlatMin, nlatMax, nlngMin, nlngMax, boundary))
        return result
    
    def CalculateAreaToAvoid(points):
        return Areas.GetBoundary(points)    

        
      
