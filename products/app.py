import sqlite3
import json
import requests
from flask import Flask, request

app = Flask(__name__)
db_name = "products.db"
sql_file = "products.sql"
db_flag = False

USER_SERVICE_URL = "http://user:5000/verify_employee"  
LOG_SERVICE_URL = "http://logs:5000/create_log"

@app.route('/', methods=(['GET']))
def index():

	return json.dumps({'1': 'test', '2': 'test2'})

@app.route('/test_micro', methods=(['GET']))
def test_micro():

	return json.dumps({"response": "This is a message from Microservice 2"})

def create_db():
    conn = sqlite3.connect(db_name)
    with open(sql_file, 'r') as sql_startup:
        init_db = sql_startup.read()
    cursor = conn.cursor()
    cursor.executescript(init_db)
    conn.commit()
    conn.close()
    global db_flag
    db_flag = True


def get_db():
    if not db_flag:
        create_db()
    conn = sqlite3.connect(db_name)
    return conn


@app.route('/create_product', methods=['POST'])
def create_product():
    jwt_token = request.headers['Authorization']
    
    headers = {"Authorization": jwt_token}
    response = requests.get(url=USER_SERVICE_URL, headers=headers)
    if response.status_code != 200 or not response.json().get("is_employee", False):
        return json.dumps({"status": 2})  
    

    username = response.json().get("username")
    name = request.form.get('name')
    price = request.form.get('price')
    category = request.form.get('category')

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                       (name, price, category))
        conn.commit()
        data = {"event_type": "product_creation", "username": username, "product_name": name}
        response = requests.post(url = LOG_SERVICE_URL, data=data)
        return json.dumps({"status": 1})
    
    finally:
        conn.close()


@app.route('/edit_product', methods=['POST'])
def edit_product():
    jwt_token = request.headers['Authorization']

    headers = {"Authorization": jwt_token}
    response = requests.get(USER_SERVICE_URL, headers=headers)

    if response.status_code != 200:
        return json.dumps({"status": 2})
    
    if not response.json().get("is_employee", False):
        return json.dumps({"status": 3})  

    username = response.json().get("username")
    product_name = request.form.get("product_name")
    new_price = request.form.get("new_price")
    new_category = request.form.get("new_category")

    try:
        conn = get_db()
        cursor = conn.cursor()

        if new_price:
            cursor.execute("UPDATE products SET price = ? WHERE name = ?", (new_price, product_name))
        elif new_category:
            cursor.execute("UPDATE products SET category = ? WHERE name = ?", (new_category, product_name))
        else:
            return json.dumps({"status": 2})  
        
        conn.commit()
        data = {"event_type": "product_edit", "username": username, "product_name": product_name}
        response = requests.post(url = LOG_SERVICE_URL, data=data)
        return json.dumps({"status": 1})
    
    finally:
        conn.close()


@app.route('/get_product_by_name', methods=['GET'])
def get_product_by_name():
    name = request.args.get('product_name')
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name, price, category FROM products WHERE name = ?", (name,))
        row = cur.fetchone()
        if not row:
            return json.dumps({"status": 3, "data": "NULL"})

        data = {
            "product_name": row[0],
            "price": row[1],
            "category": row[2]
        }
        return json.dumps({"status": 1, "data": data})
    
    finally:
        conn.close
    

@app.route('/get_products_by_category', methods=['GET'])
def get_products_by_category():
    category = request.args.get("category")
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name, price, category FROM products WHERE category = ?", (category,))
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "product_name": row[0],
                "price": row[1],
                "category": row[2]
            })
        
        return json.dumps({"status": 1, "data": result})
    
    finally:
        conn.close()

@app.route('/clear', methods=['GET'])
def clear_db():
    conn = get_db()
    cursor = conn.cursor()  
    cursor.execute("DELETE FROM products")

    conn.commit()
    conn.close()            
    return "Database cleared", 200