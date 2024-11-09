import requests


class GetAvailableCities():
    endpoint = "https://hackathon-2024.gruber-logistics.dev/Helper/GetAvailableCities"

    def get_results(self):
        response = requests.get(self.endpoint)
        return response.json()
    

class GetAvailableGoodsTypes():
    endpoint = "https://hackathon-2024.gruber-logistics.dev/Helper/GetAvailableGoodsTypes"

    def get_results(self):
        response = requests.get(self.endpoint)
        return response.json()
    
class GetAllSuppliers():
    endpoint = "https://hackathon-2024.gruber-logistics.dev/Supplier/GetAllSuppliers"

    def get_results(self):
        response = requests.get(self.endpoint)
        return response.json()
    
class GetSupplierById():
    endpoint = "https://hackathon-2024.gruber-logistics.dev/Supplier/GetSupplierById"

    def get_results(self, supplier_id):
        query = self.endpoint + f"/{supplier_id}"
        response = requests.get(query)
        return response.json()
    

class GetTransportHistoryOriginal():
    endpoint = "https://hackathon-2024.gruber-logistics.dev/Transport/GetTransportHistory"

    def get_results(self, city1, city2):
        query = self.endpoint + f"?city1={city1}&city2={city2}"
        response = requests.get(query)
        return response.json()
