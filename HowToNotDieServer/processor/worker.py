from threading import Timer
from processor.main import Processor
from processor.modeller import Modeller

WORKER_PERIOD_IN_SEC = 10
MODELLER_PERIOD_IN_SEC = 200

def OnTimer():
    try:
        Processor.PeriodicProcess()
    except:
        print("Worker exception")
    Timer(WORKER_PERIOD_IN_SEC, OnTimer).start()
    
def StartWorker():
    Timer(WORKER_PERIOD_IN_SEC, OnTimer).start()
    
def OnModellerTimer():
    try:
        Modeller.PeriodicProcess()
    except Exception as e:
            print("Failed to run Modeller, error: %s" % (e))
    Timer(MODELLER_PERIOD_IN_SEC, OnModellerTimer).start()
    
def StartModeller():
    Timer(10, OnModellerTimer).start()