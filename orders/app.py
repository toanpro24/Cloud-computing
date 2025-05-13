import json
import requests
from flask import Flask, request

app = Flask(__name__)

LOG_SERVICE_URL = "http://logs:5000/create_log"
PRODUCT_SERVICE_BY_NAME = "http://products:5000/get_product_by_name"
USER_SERVICE_URL = "http://user:5000/verify_employee"  


@app.route("/order", methods=["POST"])
def order():
    jwt = request.headers.get("Authorization")
    if not jwt:
        return json.dumps({"status": 2, "cost": "NULL"})

    headers = {"Authorization": jwt}
    response = requests.get(url=USER_SERVICE_URL, headers=headers)
    username = response.json().get("username")

   
    order_data = request.form.get("order")
    order_data = json.loads(order_data)
    total_cost = 0.0

    for item in order_data:
        product_name = item.get("product")
        quantity = item.get("quantity")

        if not product_name or quantity is None:
            return json.dumps({"status": 3, "cost": "NULL"})

        try:
            response = requests.get(url=PRODUCT_SERVICE_BY_NAME, params={"product_name": product_name})
            product_data = response.json()
        except Exception:
            return json.dumps({"status": 3, "cost": "NULL"})

        if product_data["status"] != 1:
            return json.dumps({"status": 3, "cost": "NULL"})

        price = product_data["data"]["price"]
        total_cost += price * quantity

    data = {"event_type": "order", "username": username, "product_name": product_name}
    response = requests.post(url = LOG_SERVICE_URL, data=data)
    return json.dumps({"status": 1, "cost": f"{total_cost:.2f}"})

@app.route('/clear', methods=['GET'])
def clear_db():
           
    return "Database cleared", 200