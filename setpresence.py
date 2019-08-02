import sys
import requests
import json
from lxml import etree

if __name__ == '__main__':

	if len(sys.argv) == 2:
		status = sys.argv[1]

		statusList = [ 'AVAILABLE', 'BUSY', 'DND', 'AWAY', 'UNAVAILABLE', 'VACATION']
		
		if status in statusList:
	
			if status == "AVAILABLE":
				override = 'false'
			else:
				override = 'true'
				
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
					CUSERNAME = p['CONTACT']

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

			response = requests.post('https://'+SERVER+':8083/presence-service/users/'+CUSERNAME+'/sessions', headers=headers, verify=False)

			root = etree.fromstring(response.content)

			for element in root.iter():
				if element.tag == "sessionKey":
					esessionKey = element.text

			print('End User Session Key = '+esessionKey)
			print('\n\n')

			headers = { 'Presence-Session-Key': esessionKey, 'Presence-Expiry': '3600', 'Presence-Override': override }

			presence = '<presence>'+status+'</presence>'

			root = etree.fromstring(presence)
			xml = etree.tostring(root)
			
			response = requests.put('https://'+SERVER+':8083/presence-service/users/'+CUSERNAME+'/presence/basic', data=xml, headers=headers, verify=False)

			print(response.headers)
		else: 
			print("Status must be one of AVAILABLE, BUSY, DND, AWAY, UNAVAILABLE or VACATION (case sensitive)")
	else:
		print("You need to specify a status as an argument, such as AVAILABLE, BUSY, DND, AWAY, UNAVAILABLE or VACATION (case sensitive)")


