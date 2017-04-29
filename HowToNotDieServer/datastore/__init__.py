from datastore.clients import ActiveClients
from datastore.db import GetDB

# Remove out-of-date clients
ActiveClients.RemoveAll()

# Connect DB
GetDB()