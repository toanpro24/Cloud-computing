import sqlite3
import json
import requests
from flask import Flask, request

app = Flask(__name__)

db_name = "logs.db"
sql_file = "logs.sql"  
db_flag = False

USER_SERVICE_URL = "http://user:5000/verify_employee"  


@app.route('/get_last_modifier', methods=['GET'])
def get_last_modifier():
    product_name = request.args.get("product_name")
    if not product_name:
        return json.dumps({"last_modified_by": "unknown"})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user FROM logs WHERE name = ? ORDER BY rowid DESC LIMIT 1", (product_name,))
    row = cur.fetchone()
    conn.close()

    if row:
        return json.dumps({"last_modified_by": row[0]})
    else:
        return json.dumps({"last_modified_by": "unknown"})


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

@app.route('/create_log', methods=['POST'])
def log_event():
    event_type = request.form.get("event_type")
    username = request.form.get("username")
    name = request.form.get("product_name")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (event, user, name) VALUES (?, ?, ?)", (event_type, username, name))
    conn.commit()
    conn.close()

    return "Added new event"

@app.route('/view_log', methods=['GET'])
def view_log():
    jwt_token = request.headers.get('Authorization')
    headers = {"Authorization": jwt_token}
    response = requests.get(url=USER_SERVICE_URL, headers=headers)

    if response.status_code != 200:
        return json.dumps({"status": 2, "data": "NULL"})

    requester = response.json().get("username")
    username = request.args.get("username", None)
    product = request.args.get("product", None)

    if username is not None and username != requester:
        return json.dumps({"status": 2, "data": "NULL"})

    if username:
        query = "SELECT event, user, name FROM logs WHERE user = ?"
        params = (username,)

    elif product:
        if not response.json().get("is_employee"):
            return json.dumps({"status": 3, "data": "NULL"})

        query = "SELECT event, user, name FROM logs WHERE name = ?"
        params = (product,)
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        logs = cursor.fetchall()

        result = {}
        for idx, (event, user, name) in enumerate(logs, start=1):
            result[idx] = {
                "event": event,
                "user": user,
                "name": name
            }

        return json.dumps({"status": 1, "data": result})

    finally:
        conn.close()


@app.route('/clear', methods=['GET'])
def clear_db():
    conn = get_db()
    cur = conn.cursor()  

    cur.execute("DELETE FROM logs")

    conn.commit()
    conn.close()
      
    return "Database cleared", 200