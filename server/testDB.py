from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['SFSCON24']

#test the connection
print(db)

#test the collection
print(db.list_collection_names())

negotiations = db['negotiations']

#test the collection
print(negotiations)

#retrieve all the documents
for doc in negotiations.find():
    print(doc)


#implement class as driver
class mongo_driver():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['SFSCON24']
        self.negotiations = self.db['negotiations']

    def get_all_negotiations(self):
        return self.negotiations.find()

    def post_new_negotiation(self, negotiation):
        return self.negotiations.insert_one(negotiation)
    
    def get_negotiation_by_id(self, id):
        return self.negotiations.find_one({"_id": id})
    
    def put_negotiation_by_id(self, id, negotiation):
        return self.negotiations.update_one({"_id": id}, negotiation)
    
    def delete_negotiation_by_id(self, id):
        return self.negotiations.delete_one({"_id": id})
    
    def get_ranking(self, id):
        return self.negotiations.find_one({"_id": id})["ranking"]
    
    def get_chat(self, id):
        return self.negotiations.find_one({"_id": id})["chat"]