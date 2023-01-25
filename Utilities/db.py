
import pymongo

class Database:
    def __init__(self, connectionString, databaseName, collection):
        self.connectionString = connectionString
        self.databaseName = databaseName
        self.collection = collection
        self.client = pymongo.MongoClient(self.connectionString)
    
    def connected(self):
        try:
            self.db = self.client[self.databaseName]
            self.tbl = self.db[self.collection]
        except:
            pass
        return self.db