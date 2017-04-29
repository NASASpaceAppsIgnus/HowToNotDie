from datastore.db import GetDB

class Areas:
    AREA_TO_AVOID = "areaToAvoid"
    SAFE_ZONES = "safeZones"
    DISPLAY_POLY = "displayPoly"
    DEFAULT_POSITION_RANGE_IN_DEG = 0.05
    
    def AddAreaToAvoid(leftTopPoint, rightBottomPoint, risk):
        cellsMin = GetCellIDs(leftTopPoint, 0)
        cellsMax = GetCellIDs(leftTopPoint, 0)
        areaID = "ATA" + cellsMin[0] + cellsMax[0]
        boundary = [leftTopPoint[0], leftTopPoint[1], rightBottomPoint[0], rightBottomPoint[1]]
        try:
            GetDB().Areas.delete_one({"areaID":areaID})
        except:
            pass
        
        try: 
            GetDB().Areas.insert_one({"areaID":areaID, "type":Areas.AREA_TO_AVOID, "data":{"boundary":boundary,"risk":risk}})
            cellIDs = GetCellIDsWithBoundary(boundary)
            for cellID in cellIDs:
                cell = GetDB().Cells.find_one({"cellID":cellID})
                if cell:
                    if areaID not in cell["areas"]:
                        cell["areas"].append({"areaID":areaID})
                        GetDB().Cells.update_one({"cellID":cellID}, {"$set":{"areas":cell["areas"]}})
                else:
                    GetDB().Cells.insert_one({"cellID":cellID, "type":Areas.AREA_TO_AVOID, "data":{"boundary":boundary,"risk":risk}})
                GetDB().Cells.insert_one({"cellID":cellID, "areas":[areaID]})

        except Exception as e:
            print("Failed to add area to avoid: %s, error: %s" % (boundary, e)) 
            
    #def RemoveAreaToAvoid():
        
    
    def Load(position, data):
        data[Areas.AREA_TO_AVOID]=[]
        data[Areas.SAFE_ZONES]=[]
        data[Areas.DISPLAY_POLY]=[]
        
        try: 
            cellIDs = Areas.GetCellIDs(position, Areas.DEFAULT_POSITION_RANGE_IN_DEG)
            for cellID in cellIDs:
                cell = GetDB().Cells.find_one({"cellID":cellID})
                if cell:
                    for areaID in cell["areas"]:
                        area = GetDB().Areas.find({"areaID":areaID})
                        areaType = area["type"]
                        data[areaType].append(area["data"])

        except Exception as e:
            print("Failed to Load areas: %s, error: %s" % (position, e))
            
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
        lat = position[0]
        lng = position[1]
        #boundary box
        latMin = lat - range
        lngMin = lng - range
        latMax = lat + range
        lngMax = lng + range
        boundary = [latMin, lngMin, latMax, lngMax]
        return GetCellIDsWithBoundary(boundary)
    
    def GetCellIDsWithBoundary(boundary):
        result = []
        nlatMin = NormLat(boundary[0])
        nlngMin = NormLng(boundary[1])
        nlatMax = NormLat(boundary[2])
        nlngMax = NormLng(boundary[3])
        for i in range(nlatMin, nlatMax):
            for j in range(nlngMin, nlngMax):
                result.append(str(i) + str(j))
        return result

        
      