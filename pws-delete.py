"""pws-delete.py deletes the setup created by pws-create.py

The settings created by pws-create.py will expire based on the Expiry
value in the header (see pws-create.py comments for an explanation), so this
script isn't necessary unless you want to back out of the pws-create.py
settings in order to change how pws-create.py works.

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

if __name__ == '__main__':

# Get the necessary data, such as the server, username/password of the
# application user and username of the end user

	with open('serverparams.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			SERVER = p['SERVER']

	with open('appuser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			AUSERNAME = p['USERNAME']
			APASSWORD = p['PASSWD']

	with open('enduser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			EUSERNAME = p['USERNAME']

# Log in as the application user to get the application user session key
# There are two ways to log in.  One forces Cisco IM&P to create a new
# session key every time, the other allows you to repeat this request
# and get the same session key every time.  We're using the latter method.
# See (https://developer.cisco.com/site/im-and-presence/documents/presence_web_service/latest_version/)
# for the differences between the two methods.

	passwordxml = '<session><password>'+APASSWORD+'</password></session>'

	root = etree.fromstring(passwordxml)
	xml = etree.tostring(root)

	headers = { 'Content-Type':'text/xml' }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+AUSERNAME+'/sessions', headers=headers, data=xml, verify=False)

	root = etree.fromstring(response.content)

	for element in root.iter():
		if element.tag == "sessionKey":
			asessionKey = element.text

	print('\n\n')
	print('App User Session Key = '+asessionKey)
	print('\n\n')

# Log in as the end user to get the end user session key
# There are two ways to log in.  One forces Cisco IM&P to create a new
# session key every time, the other allows you to repeat this request
# and get the same session key every time.  We're using the latter method.
# See (https://developer.cisco.com/site/im-and-presence/documents/presence_web_service/latest_version/)
# for the differences between the two methods.

	headers = { 'Presence-Session-Key': asessionKey }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/sessions', headers=headers, verify=False)

	root = etree.fromstring(response.content)

	for element in root.iter():
		if element.tag == "sessionKey":
			esessionKey = element.text

# Use the end user session key to unsubscribe to presence notifications

# Technically, you should only have to delete subscription 1.
# Deleting subscriptions 1-4 is overkill, but it's a way to guarantee that you
# remove all subscriptions you may have accidentally created by running pws-create.py
# multiple times

	headers = { 'Presence-Session-Key': esessionKey }

	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/1', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/2', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/3', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/4', headers=headers, verify=False)

# Use the application user session key to delete the endpoint definition

# Technically, you should only have to delete endpoint 1.
# Deleting endpoints 1-4 is overkill, but it's a way to guarantee that you
# remove all endpoints you may have accidentally created by running pws-create.py
# multiple times

	headers = { 'Presence-Session-Key': asessionKey }

	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/1', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/2', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/3', headers=headers, verify=False)
	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/4', headers=headers, verify=False)
