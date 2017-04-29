from threading import Timer
from processor.main import Processor

WORKER_PERIOD_IN_SEC = 10

def OnTimer():
    try:
        Processor.PeriodicProcess()
    except:
        print("Worker exception")
    Timer(WORKER_PERIOD_IN_SEC, OnTimer).start()
    
def StartWorker():
    Timer(WORKER_PERIOD_IN_SEC, OnTimer).start()