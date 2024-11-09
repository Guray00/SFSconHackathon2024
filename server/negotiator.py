from pymongo import MongoClient
from main_server import GetAvailableCities
from main_server import GetSupplierById

client = MongoClient('localhost', 27017)

db = client['SFSCON24']
