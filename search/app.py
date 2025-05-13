import json
import requests
from flask import Flask, request

app = Flask(__name__)
PRODUCT_SERVICE_BY_NAME = "http://products:5000/get_product_by_name"
PRODUCT_SERVICE_BY_CATEGORY = "http://products:5000/get_products_by_category"
LOGGING_SERVICE_URL = "http://logs:5000/get_last_modifier"
USER_SERVICE_URL = "http://user:5000/verify_employee"  
CREATE_LOG_SERVICE_URL = "http://logs:5000/create_log"


@app.route('/', methods=(['GET']))
def index():

	return json.dumps({'1': 'test', '2': 'test2'})

@app.route('/test_micro', methods=(['GET']))
def test_micro():

	return json.dumps({"response": "This is a message from Microservice 2"})
    


@app.route('/search', methods=['GET'])
def search_product():
    jwt = request.headers.get("Authorization")
    if not jwt:
        return json.dumps({"status": 2, "data": "NULL"})
    
    headers = {"Authorization": jwt}
    response = requests.get(url=USER_SERVICE_URL, headers=headers)

    username = response.json().get("username")
    product_name = request.args.get("product_name", None)
    category = request.args.get("category", None)

    result = []
    if product_name:
        r = requests.get(PRODUCT_SERVICE_BY_NAME, params={'product_name': product_name})
        if r.status_code != 200 or r.json().get("status") != 1:
            return json.dumps({"status": 3, "data": "NULL"})
        product = r.json().get("data")
        result = [product] if isinstance(product, dict) else product
    else:
        r = requests.get(PRODUCT_SERVICE_BY_CATEGORY, params={"category": category})
        if r.status_code != 200 or r.json().get("status") != 1:
            return json.dumps({"status": 3, "data": "NULL"})
        result = r.json().get("data")

    if result:
        for product in result:
            name = product.get("product_name")
            log_res = requests.get(LOGGING_SERVICE_URL, params={'product_name': name})
            log_res = log_res.json()
            last_mod = log_res.get("last_modified_by", "unknown")
            product["last_mod"] = last_mod
            data = {"event_type": "search", "username": username, "product_name": name}
            response = requests.post(url = CREATE_LOG_SERVICE_URL, data=data)
    return json.dumps({"status": 1, "data": result})


@app.route('/clear', methods=['GET'])
def clear_db():
    
    return "Database cleared", 200