from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import requests
import numpy as py
import utility

from testDB import mongo_driver_negotiate


from flask_cors import CORS, cross_origin

app = Flask(__name__)
api = Api(app)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

class MainServer(Resource):
    def get(self):
        return jsonify({"message": "Hello, World!"})
    
    def post(self):
        data = request.get_json()
        return jsonify(data)
    

class suppliers(Resource):
    def get(self):
        city1 = request.args.get("city1")
        city2 = request.args.get("city2")

        country1 = request.args.get("country1")
        country2 = request.args.get("country2")

        #api to be called doesn't differentiate between loading and unloading address 
        endpoint = ""
        if city1:
            endpoint = f"/Transport/GetTransportHistory?city1={city1}"
            if city2:
                endpoint += f"&city2={city2}"
        if country1:
            if not endpoint:
                endpoint = f"/Transport/GetTransportHistory?country1={country1}"
            else:
                endpoint += f"&country1={country1}"
            if country2:

                endpoint += f"&country2={country2}"

        complete_endpoint = "https://hackathon-2024.gruber-logistics.dev"+endpoint

        #perform a get request to the endpoint and get results as json
        response = requests.get(complete_endpoint)

        #city_1 and country_1 should be considered as loading address
        #city_2 and country_2 should be considered as unloading address

        data = response.json()

        return jsonify(data)

        #keep only data that fits the criteria
        filtered_data = []

        #for now we consider only city1 and city2
        for i in data:
            if i["loadingAddress"]["city"] == city1 and i["unloadingAddress"]["city"] == city2:
                filtered_data.append(i)

        return jsonify(filtered_data)
    
    def post(self):
        data = request.get_json()
        return jsonify(data)
    

class GetTransportHistory():
    def get(self, loading_address, unloading_address):
        if not loading_address or not unloading_address:
            return jsonify({"message": "Please provide loading and unloading address"})
        
        data = utility.GetTransportHistoryOriginal().get_results(loading_address, unloading_address)

        if not data:
            return None


        filtered_data = []
        for i in data:
            if i["loadingAddress"]["city"] == loading_address and i["unloadingAddress"]["city"] == unloading_address:
                filtered_data.append(i)

        #return as json
        return filtered_data
    




class negotiations(Resource):
    def get(self):
        
        #check if there are any parameters
        status = request.args.get("status")

        mongo = mongo_driver_negotiate()

        if status:
            query = mongo.get_by_status(status)
        else:
            query = mongo.get_all_negotiations()

        data = []
        for i in query:
            #remove the _id field
            i.pop("_id")
            data.append(i)

        mongo.close()

        return data

    
    #Work In Progress
    def post(self):
        load_city = request.args.get("load_city")
        unload_city = request.args.get("unload_city")
        
        min_price = request.args.get("min_price")
        max_price = request.args.get("max_price")
        requested_date = request.args.get("date")
       

        if not load_city or not unload_city:
            return jsonify({"message": "Please provide loading and unloading city"})
        
        #perform the query to get the history of transport between the two cities

        data = GetTransportHistory().get(load_city, unload_city)

        #if there are no results, return a string syaing that there are no results
        if not data:
            return jsonify({"message": "No results found for this route"})


        # group by supplier id
        map_price_list = {}
        map_perf_list = {}
        for item in data:
            supplierId = item["supplierId"]
            curr_price = item["price"]
            curr_perf = item["performanceScore"]
            if supplierId not in map_price_list:
                map_price_list[supplierId] = []
            if supplierId not in map_perf_list:
                map_perf_list[supplierId] = []
            map_price_list[supplierId].append(curr_price)
            map_perf_list[supplierId].append(curr_perf)

        # rank calculations and sorting
        rank = []
        for item in data:
            curr_list = []

            supplierId = item["supplierId"]
            curr_list.append(supplierId)

            curr_rank = CalculateRank().get(map_price_list[supplierId], map_perf_list[supplierId], 0.6, 0.4)
            curr_list.append(curr_rank)

            rank.append(curr_list)

        rank.sort(key=lambda x: x[1], reverse=True)

        mapped_rank = MapToContacts().get(rank)
        


        #sort rank by alhabetuical order
        mapped_rank.sort(key=lambda x: x["name"])

        data = {
            "date": requested_date,
            "minimum_price": min_price,
            "maximum_price": max_price,
            "load_city": load_city,
            "unload_city": unload_city,
            "rank": mapped_rank,
            "status": "pending"
        }




        llm_host = "http://192.168.127.161:8080/receive_params"

        #send data to LLM using post request, setting header bypass-tunnel-reminder
        # also set and send a custom / non-standard browser User-Agent request header
        #print the response code
        mongo = mongo_driver_negotiate()

        #add status field to data
        data["status"] = "pending"
        negotiation_id = mongo.post_new_negotiation(data.copy()).inserted_id


        #set timeout to 5 minutes
        response = requests.post(llm_host, json=data, timeout=(60,300))

        #response from LLM contains the outcome of the negotiation
        response_data = response.json()

        if response_data["final_status"] == "success":
            #update the negotiation status
            mongo.put_negotiation_by_id(negotiation_id, {"status": "accepted", "final_price":response_data["final_price"]}) 
        else:
            mongo.put_negotiation_by_id(negotiation_id, {"status": "rejected"})

        mongo.close()

        #should return price and supplier name
        return {"final_price": response_data["final_price"], "supplier_name": response_data["supplier_name"]}

class MapToContacts():
    def get(self, rank_list):
        res = []
        for item in rank_list:
            supplierId = item[0]
            supplierData = utility.GetSupplierById().get_results(supplierId)
            data = {"name": supplierData["name"], "language": supplierData["language"]}
            res.append(data)
        return res

    
class CalculateRank():
    def get(self, price_list, perf_list, weight_price, weight_perf):
        
        max_price = max(price_list)
        max_perf = max(perf_list)
        min_price = min(price_list)
        min_perf = min(perf_list)
        avg_price = py.mean(price_list)
        avg_perf = py.mean(perf_list)

        norm_price = float(avg_price - min_price) / (max_price - min_price) if max_price - min_price != 0 else 0
        norm_perf = float(avg_perf - min_perf) / (max_perf - min_perf) if max_perf - min_perf != 0 else 0
        return weight_price * norm_price + weight_perf * norm_perf


class averagePrice(Resource):
    def get(self):
        start_city = request.args.get("start_city")
        end_city = request.args.get("end_city")

        if not start_city or not end_city:
            return jsonify({"message": "Please provide start and end city"})
        
        #requests to GetTransportHistory
        data = requests.get("localhost:5000/GetTransportHistory?load_city="+start_city+"&unload_city="+end_city).json()

        #get the average price for the transport between the two cities
        price_list = []
        for item in data:
            price_list.append(item["price"])

        avg_price = py.mean(price_list)
        
        return jsonify({"average_price": avg_price})

        
       
class confirmNegotiation(Resource):
    def post(self):
        #should receive negotiation id
        negotiation_id = request.args.get("negotiation_id")
        if not negotiation_id:
            return jsonify({"message": "Please provide negotiation id"})
        
        mongo = mongo_driver_negotiate()
        negotiation = mongo.get_negotiation_by_id(negotiation_id)
        if not negotiation:
            return jsonify({"message": "Negotiation not found"})
        negotiation["status"] = "confirmed"
        mongo.put_negotiation_by_id(negotiation_id, negotiation)


        mongo.close()

        return jsonify({"message": "Negotiation accepted"})
    

class GetAvailableCities(Resource):
    @cross_origin()
    def get(self):
        return utility.GetAvailableCities().get_results()
    

class GetAveragePrice(Resource):
    def get(self):
        start_city = request.args.get("start_city")
        end_city = request.args.get("end_city")

        if not start_city or not end_city:
            return jsonify({"message": "Please provide start and end city"})
        
        #requests to GetTransportHistory
        data = GetTransportHistory().get(start_city, end_city)
        #compute the average price
        price_list = []
        for item in data:
            price_list.append(item["price"])

        avg_price = py.mean(price_list)

        return jsonify({"average_price": avg_price})


api.add_resource(MainServer, "/")
api.add_resource(suppliers, "/suppliers")
api.add_resource(negotiations, "/negotiations")
api.add_resource(averagePrice, "/averagePrice")
api.add_resource(confirmNegotiation, "/confirmNegotiation")
api.add_resource(GetAvailableCities, "/GetAvailableCities")
api.add_resource(GetAveragePrice, "/GetAveragePrice")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=9000)
