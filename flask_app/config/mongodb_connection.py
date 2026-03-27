from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os

class MongoDBConnection:
    def __init__(self, db_name):
        self.uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name
        try:
            # Set a short timeout for the demo hackathon
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            # Trigger a simple command to check connection
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.available = True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            print(f"WARNING: MongoDB not found at {self.uri}. Persistence may fail.")
            self.available = False
            self.db = None

    def get_collection(self, collection_name):
        if not self.available:
            return None
        return self.db[collection_name]

def connectToMongo(db_name="white_travels_db"):
    return MongoDBConnection(db_name)
