import requests
import json
from lxml import etree

if __name__ == '__main__':


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
	print('\n\n')

	headers = { 'Presence-Session-Key': asessionKey }

	response = requests.post('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/sessions', headers=headers, verify=False)

	root = etree.fromstring(response.content)

	for element in root.iter():
		if element.tag == "sessionKey":
			esessionKey = element.text

	headers = { 'Presence-Session-Key': esessionKey }

	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/1', headers=headers, verify=False)

	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/2', headers=headers, verify=False)

	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	response = requests.delete('https://'+SERVER+':8083/presence-service/users/'+EUSERNAME+'/subscriptions/3', headers=headers, verify=False)

	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	headers = { 'Presence-Session-Key': asessionKey }

	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/1', headers=headers, verify=False)
	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/2', headers=headers, verify=False)
	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/3', headers=headers, verify=False)
	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

	response = requests.delete('https://'+SERVER+':8083/presence-service/endpoints/4', headers=headers, verify=False)
	print('\n\n')
	print(response.text)
	print(response.content)
	print(response.headers)
	print('\n\n')

