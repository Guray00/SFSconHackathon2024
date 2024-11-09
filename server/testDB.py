from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)

db = client['SFSCON24']

#test the connection


#implement class as driver
class mongo_driver_negotiate():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['SFSCON24']
        self.negotiations = self.db['negotiations']

    def get_all_negotiations(self):
        return self.negotiations.find()

    def post_new_negotiation(self, negotiation):
        return self.negotiations.insert_one(negotiation)

    def get_negotiation_by_id(self, id):
        return self.negotiations.find_one({"_id": ObjectId(id)})

    def put_negotiation_by_id(self, id, negotiation):
        return self.negotiations.update_one({"_id": ObjectId(id)}, {"$set": negotiation})

    def delete_negotiation_by_id(self, id):
        return self.negotiations.delete_one({"_id": ObjectId(id)})

    def get_ranking(self, id):
        return self.negotiations.find_one({"_id": ObjectId(id)})["ranking"]

    def get_chat(self, id):
        return self.negotiations.find_one({"_id": ObjectId(id)})["chat"]

    def get_by_status(self, status):
        return self.negotiations.find({"status": status})

    
    #close the connection
    def close(self):
        self.client.close()
    