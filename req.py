import requests
import json
from lxml import etree

if __name__ == '__main__':

# Get all the necessary user information for the server, cucm admin, adminuser, enduser

	with open('serverparams.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			SERVER = p['SERVER']
			USERNAME = p['USERNAME']
			PASSWD = p['PASSWD']
			ENDPOINTURL = p['ENDPOINTURL']

	with open('appuser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			AUSERNAME = p['USERNAME']
			APASSWORD = p['PASSWD']

	with open('enduser.json') as json_file:
		data = json.load(json_file)
		for p in data['params']:
			EUSERNAME = p['USERNAME']


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

	headers = { 'Presence-Session-Key': asessionKey }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/sessions', headers=headers, verify=False)

	root = etree.fromstring(response.content)

	for element in root.iter():
		if element.tag == "sessionKey":
			esessionKey = element.text

	print('End User Session Key = '+esessionKey)
	print('\n\n')

	headers = { 'Presence-Session-Key': asessionKey, 'Presence-Expiry': '3600' }

	print("End Point = " + ENDPOINTURL)
	print('\n\n')

	endpointxml = '<endpoint><url>'+ENDPOINTURL+'</url></endpoint>'

	root = etree.fromstring(endpointxml)
	xml = etree.tostring(root)

	response = requests.post('https://'+SERVER+':8083/presence-service/endpoints', headers=headers, data=xml, verify=False)

	ENDPOINTID = response.headers['Location'][-1]
	print('Endpoint ID = '+ENDPOINTID)


# The object in this next section is to build a subscription list something like this:

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

	print(response.text)
	print(response.content)
	print(response.headers)
	SUBSCRIPTIONID = response.headers["location"][-1]
	print('Subscription ID = '+SUBSCRIPTIONID)
	print('\n\n')

