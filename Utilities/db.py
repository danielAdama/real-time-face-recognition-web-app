import numpy as np
import pymongo
import ast


class Database:
    def __init__(self, connectionString, databaseName, collection):
        self.connectionString = connectionString
        self.databaseName = databaseName
        self.collection = collection
        self.client = pymongo.MongoClient(self.connectionString)
        self.face = {}
    
    def connected(self):
        try:
            self.db = self.client[self.databaseName]
            self.tbl = self.db[self.collection]
        except:
            pass
        return self.db
    
    def processed_data(self):
        cursor = self.connected().UserEncoding.find({}, {"_id":0})
        data = [document for document in cursor]
        self.face["names"] = [i["Name"] for i in data]
        self.face["encodingArr"] = [np.array(ast.literal_eval(field["Encoding"])) for field in data]
        return self.face