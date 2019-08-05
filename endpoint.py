"""endpoint.py is a web service listener for updates to a contact's presence

Copyright (c) 2018 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
import json
from lxml import etree
from flask import Flask, request

# We use "flask" to create the web service to respond to presence notifications
# We use "requests" to execute REST operations to get presenced status
# We use "lxml" to manipulate XML into data that "requests" can use
# We use "json" to read in json files with data such as server, username, password

app = Flask(__name__)

# This endpoint web service responds to a GET REST request
# that notifies us that a presence status has changed

@app.route('/pws',methods=['GET'])
def pws():
	id = str(request.args.get('id'))
	etype = str(request.args.get('eventType'))
	headers = { 'Presence-Session-Key': esessionKey }

# If this is truly a PRESENCE_NOTIFICATION, then fetch (GET) the presence information

# This app does not do anything fancy.  It just appends the presence information
# to a file for demonstration purposes

	if etype == "PRESENCE_NOTIFICATION":
		response = requests.get('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/presence/basic/subscriptions/'+id, headers=headers, data=xml, verify=False)
		with open('status.txt','a+') as fh:
			fh.write(response.text)
			fh.close()
		return(response.text)
	return("Got Random GET")

@app.errorhandler(404)
def not_found(error):
    return(error)

if __name__ == "__main__":

# Go through the normal process of logging in the app user,
# get the app user session key, use it to log in the end user,
# get the end user session key, and then fetch (GET) the
# current presence.  This is a good practice because there
# might be a pending presence update, and you have to "clear"
# that for the web service presecne notifications to come in.

# Load all the server, user, and password information

	with open('serverparams.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			SERVER = p['SERVER']
			USERNAME = p['USERNAME']
			PASSWD = p['PASSWD']
			ENDPOINTURL = p['ENDPOINTURL']
			HOST = p['HOST']

	with open('appuser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			AUSERNAME = p['USERNAME']
			APASSWORD = p['PASSWD']

	with open('enduser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			EUSERNAME = p['USERNAME']

# Log in the app user

	passwordxml = '<session><password>'+APASSWORD+'</password></session>'

	root = etree.fromstring(passwordxml)
	xml = etree.tostring(root)

	headers = { 'Content-Type':'text/xml' }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+AUSERNAME+'/sessions', headers=headers, data=xml, verify=False)

	root = etree.fromstring(response.content)

# Get the app user session key

	for element in root.iter():
		if element.tag == "sessionKey":
			asessionKey = element.text

	print('\n\n')
	print('App User Session Key = '+asessionKey)

	headers = { 'Presence-Session-Key': asessionKey }

# Use the app user session key and end user username
# to get the end user session key

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/sessions', headers=headers, verify=False)

	root = etree.fromstring(response.content)

	for element in root.iter():
		if element.tag == "sessionKey":
			esessionKey = element.text

	print('End User Session Key = '+esessionKey)
	print('\n\n')

# Use the end user session key to fetch (GET) the latest presence information
# and write it to the status.txt file.
# This assumes the subscription ID is 1, which is not a safe assumption
# under normal circumstances, but it works for the purpose of this demo

	headers = { 'Presence-Session-Key': esessionKey }

	response = requests.get('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/presence/basic/subscriptions/1', headers=headers, data=xml, verify=False)
	print(response.content)
	with open('status.txt','a+') as fh:
		fh.write(response.text)
		fh.close()

	app.run(host=HOST)
