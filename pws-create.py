"""pws-create.py sets up Cisco IM&P to notify endpoint.py of a user's presence changes

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
			HOST = p['HOST']

# Set the endpoint URL - this is the Presence Web Service that will
# receive notifications that presence for a user has changed

	ENDPOINTURL = 'http://' + HOST + ':5000/pws'

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

	print('End User Session Key = '+esessionKey)
	print('\n\n')

# Use the application user session key to tell Cisco IM&P where
# the endpoint (Presence Web Service) listener is (endpoint URL)

	headers = { 'Presence-Session-Key': asessionKey, 'Presence-Expiry': '3600' }

	print("End Point = http://" + ENDPOINTURL + ':5000/pws')
	print('\n\n')

	endpointxml = '<endpoint><url>'+ENDPOINTURL+'</url></endpoint>'

	root = etree.fromstring(endpointxml)
	xml = etree.tostring(root)

	response = requests.post('https://'+SERVER+':8083/presence-service/endpoints', headers=headers, data=xml, verify=False)

	ENDPOINTID = response.headers['Location'][-1]
	print('Endpoint ID = '+ENDPOINTID)

# Use the end user session key to subscribe to presence notifications for
# one or more contacts

# The object in this next section is to build a subscription list something
# like this from the contacts.list file:

#<subscription>
#	<contactsList>
#		<contact contactURI="enduser1@cisco.com"/>
#		<contact contactURI="enduser2@cisco.com"/>
#		<contact contactURI="enduser3@cisco.com"/>
#	</contactsList>
#	<subscriptionType>PRESENCE_NOTIFICATION</subscriptionType>
#	<endPointID>{endpoint-id}</endPointID>
#</subscription>

	with open('contacts.list','rb') as fh:
		contacts = json.load(fh)

# Read in the list of contacts for whom we want presence updates
# Wrap them in the XML tag

	setcontacts=[]
	length=len(contacts)
	for i in range(length):
		setcontacts.append('<contact contactURI="'+contacts[i]+'@'+SERVER+'"/>')

	contactxml='<subscription><contactsList>'

	for i in range(length):
		contactxml = contactxml+setcontacts[i]

	contactxml = contactxml+'</contactsList><subscriptionType>PRESENCE_NOTIFICATION</subscriptionType><endPointID>'+ENDPOINTID+'</endPointID></subscription>'
	print(contactxml)

	root = etree.fromstring(contactxml)
	xml = etree.tostring(root)

	headers = { 'Presence-Session-Key': esessionKey, 'Presence-Expiry': '3600' }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions', headers=headers, data=xml, verify=False)

# For the purposes of testing, the SUBSCRIPTIONID should always be "1".  If
# you get anything other than "1" then you probably ran this script
# multiple times without deleting the information with the script
# pws-delete.py in order to clear the endpoint and subscriptions before
# testing again.

	print(response.text)
	print(response.content)
	print(response.headers)
	SUBSCRIPTIONID = response.headers["location"][-1]
	print('Subscription ID = '+SUBSCRIPTIONID)
	print('\n\n')
