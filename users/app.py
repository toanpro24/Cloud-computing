import sqlite3
import os
import json
import re
import base64
import hmac
import hashlib
import requests
from flask import Flask, request

app = Flask(__name__)

db_name = "user.db"
sql_file = "user.sql"
db_flag = False

LOG_SERVICE_URL = "http://logs:5000/create_log"


@app.route('/', methods=(['GET']))
def index():
	MICRO2URL = "http://localhost:9001/test_micro"
	r = requests.get(url = MICRO2URL)
	data = r.json()

	return data


@app.route('/test_micro', methods=(['GET']))
def test_micro():

	return "This is Microservice 1"


def get_secret_key():
    with open("key.txt", "r") as key_file:
        return key_file.readline().strip()


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

def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8')

def base64_url_decode(data):
    padding = '=' * (4 - len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_jwt_token(username):
    secret_key = get_secret_key()
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "username": username,
    }

    header_encoded = base64_url_encode(json.dumps(header).encode('utf-8'))
    payload_encoded = base64_url_encode(json.dumps(payload).encode('utf-8'))
    signature_input = f"{header_encoded}.{payload_encoded}".encode('utf-8')
    signature = hmac.new(secret_key.encode('utf-8'),
                         signature_input, hashlib.sha256).hexdigest()

    jwt_token = f"{header_encoded}.{payload_encoded}.{signature}"
    return jwt_token


def verify_jwt_token(jwt_token):
    secret_key = get_secret_key()
    try:
        header_encoded, payload_encoded, signature_provided = jwt_token.split('.')
        header = json.loads(base64_url_decode(header_encoded))
        payload = json.loads(base64_url_decode(payload_encoded))
        signature_input = f"{header_encoded}.{payload_encoded}".encode('utf-8')
        expected_sig = hmac.new(secret_key.encode('utf-8'), signature_input, hashlib.sha256).hexdigest()

        if expected_sig != signature_provided:
            return False, "Invalid signature"

        return True, payload

    except Exception as e:
        return False, str(e)


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def user_exists(field, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user WHERE {field} = ?", (value,))
    found = cursor.fetchone() is not None
    conn.close()
    return found


def validate_password(password, first_name, last_name, username):
    if len(password) < 8:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if username in password or first_name in password or last_name in password:
        return False
    return True

#Taken from project 2
@app.route('/create_user', methods=['POST'])
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email_address = request.form['email_address']
    employee = request.form['employee']
    password = request.form['password']
    salt = request.form['salt']

    if user_exists("username", username):
        return json.dumps({"status": 2, "pass_hash": "NULL"})

    if user_exists("email_address", email_address):
        return json.dumps({"status": 3, "pass_hash": "NULL"})

    is_valid = validate_password(password, first_name, last_name, username)
    if not is_valid:
        return json.dumps({"status": 4, "pass_hash": "NULL"})

    pass_hash = hash_password(password, salt)

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (first_name, last_name, username, email_address, employee, password, salt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (first_name, last_name, username, email_address, employee, pass_hash, salt))
        conn.commit()
        data = {"event_type": "user_creation", "username": username, "product_name": "NULL"}
        response = requests.post(url = LOG_SERVICE_URL, data=data)
        return json.dumps({"status": 1, "pass_hash": pass_hash})

    finally:
        conn.close()

#Taken from project 2
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password, salt FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user is None:
            return json.dumps({"status": 2, "jwt": "NULL"})

        pass_hash, salt = user
        if hash_password(password, salt) != pass_hash:
            return json.dumps({"status": 2, "jwt": "NULL"})

        jwt_token = create_jwt_token(username)
        data = {"event_type": "login", "username": username, "product_name": "NULL"}
        response = requests.post(url = LOG_SERVICE_URL, data=data)
        return json.dumps({"status": 1, "jwt": jwt_token})

    finally:
        conn.close()


@app.route('/verify_employee', methods=['GET'])
def verify_employee():
    jwt_token = request.headers.get('Authorization')
    is_valid, payload = verify_jwt_token(jwt_token)
    
    if not is_valid:
        return json.dumps({"is_employee": False})

    username = payload.get("username") 

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee FROM user WHERE username = ?", (username,))
        is_employee = cursor.fetchone()[0]
        if str(is_employee).lower() == "false" or is_employee in (0, False):
            return json.dumps({"is_employee": False})
            
        return json.dumps({"is_employee": True, "username": username})
    finally:
        conn.close()


@app.route('/clear', methods=['GET'])
def clear_db():
    conn = get_db()
    cursor = conn.cursor()  
    cursor.execute("DELETE FROM user")

    conn.commit()
    conn.close()             
    return "Database cleared", 200
