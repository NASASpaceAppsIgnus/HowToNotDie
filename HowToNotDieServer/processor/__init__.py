from processor.worker import StartWorker, StartModeller
from datastore.firepoints import FirePoints

# Start background processings
StartWorker()
StartModeller()
FirePoints.Load()