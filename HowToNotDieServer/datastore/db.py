from pymongo import MongoClient

dbClient = None

def GetDB():
    global dbClient
    if not dbClient:
        dbClient = MongoClient('mongodb://localhost:27017/')
    return dbClient.HowToNotDieDB