"""setpresence.py sets the presence of the contact defined in enduser.json

Usage: python setpresence.py <one of AVAILABLE, BUSY, DND, AWAY, UNAVAILABLE or VACATION>

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
import sys
import requests
import json
from lxml import etree

if __name__ == '__main__':

	if len(sys.argv) == 2:
		status = sys.argv[1]

		statusList = [ 'AVAILABLE', 'BUSY', 'DND', 'AWAY', 'UNAVAILABLE', 'VACATION']

		if status in statusList:

# Override sets the presence even if you are running another client that has
# a presence already set.  Otherwise, that client will continue to use its
# current presence setting.  But override must be "false" if you're setting
# the presence to AVAILABLE

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
