import requests
import json
import os

try:
	
	URLCREATEUSER = "http://127.0.0.1:9000/create_user"
	URLLOGIN = "http://127.0.0.1:9000/login"
	URLPRODUCTCREATE = "http://127.0.0.1:9001/create_product"
	URLPRODUCTEDIT = "http://127.0.0.1:9001/edit_product"
	URLSEARCH = "http://127.0.0.1:9002/search"
	URLORDER = "http://127.0.0.1:9003/order"
	URLLOG = "http://127.0.0.1:9004/view_log"

	URLUSERclear = "http://127.0.0.1:9000/clear"
	URLPRODUCTclear = "http://127.0.0.1:9001/clear"
	URLSEARCHclear = "http://127.0.0.1:9002/clear"
	URLORDERclear = "http://127.0.0.1:9003/clear"
	URLLOGclear = "http://127.0.0.1:9004/clear"
	r_clear = requests.get(url = URLUSERclear)
	r_clear = requests.get(url = URLPRODUCTclear)
	r_clear = requests.get(url = URLSEARCHclear)
	r_clear = requests.get(url = URLORDERclear)
	r_clear = requests.get(url = URLLOGclear)


	PARAMS = {'first_name': 'james', 'last_name': 'mariani', 'username': 'jmm', 'email_address': 'j@a.com', 'password': 'Examplepassword1', 'employee': True, 'salt': 'FE8x1gO+7z0B'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		quit()
	
	PARAMS = {'first_name': 'abigail', 'last_name': 'murray', 'username': 'murra', 'email_address': 'a@a.com', 'password': 'Examplepassword1', 'employee': True, 'salt': 'K8ENdhu#nxe3'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		quit()

	PARAMS = {'first_name': 'griffin', 'last_name': 'klevering', 'username': 'griff', 'email_address': 'g@g.com', 'password': 'Examplepassword1', 'employee': False, 'salt': 'xaxkRSzNPnP4'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		quit()


	LOGINPARAMS = {'username': 'jmm', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'}
	for key in solution:
		if solution[key] != login_data[key]:
			quit()
	
	LOGINPARAMS = {'username': 'murra', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJtdXJyYSJ9.21b8cb34f256fda21992cb1cedf43869a1f81bfb8802581b9091960b6165db43'}
	for key in solution:
		if solution[key] != login_data[key]:
			quit()

	LOGINPARAMS = {'username': 'griff', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZiJ9.b5d00c0a804f967bacfb3a5187d4fd501490f968261511686514de2f21cc5e2b'}
	for key in solution:
		if solution[key] != login_data[key]:
			quit()

	print('Test Passed')

except:
	print('Test Failed')

