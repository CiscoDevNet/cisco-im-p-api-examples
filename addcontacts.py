"""addcontacts.py adds contacts to a user's Jabber account

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
import json
import requests

from lxml import etree
from requests import Session
from requests import post
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault

# We use "zeep" to execute SOAP requests
# We use "requests" to execute REST operations to get presenced status
# We use "lxml" to manipulate XML into data that "requests" can use
# We use "json" to read in json files with data such as server, username, password

# This class lets you view the incoming and outgoing http headers and/or XML

class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))

if __name__ == '__main__':

# Get all the necessary user information for the server, cucm admin, adminuser, enduser

    with open('serverparams.json') as json_file:
        data = json.load(json_file)
        for p in data['params']:
            SERVER = p['SERVER']
            USERNAME = p['USERNAME']
            PASSWD = p['PASSWD']

    with open('appuser.json') as json_file:
        data = json.load(json_file)
        for p in data['params']:
            AUSERNAME = p['USERNAME']
            APASSWD = p['PASSWD']

    with open('enduser.json') as json_file:
        data = json.load(json_file)
        for p in data['params']:
            EUSERNAME = p['USERNAME']

    SERVER_URL = 'https://' + SERVER + ':8443/EPASSoap/service/v105'
    WSDL_URL = 'https://' + SERVER + '/EPASSoap/service/latest?wsdl'

    # history shows http_headers
    history = HistoryPlugin()

    # This is where the meat of the application starts
    # The first step is to create a SOAP client session
    session = Session()

    # We avoid certificate verification by default, but you can set your certificate path
    # here instead of the False setting
    session.verify = False
    session.auth = HTTPBasicAuth(USERNAME, PASSWD)

    transport = Transport(session=session, timeout=10, cache=SqliteCache())

    # strict=False is not always necessary, but it allows zeep to parse imperfect XML
    settings = Settings(strict=False, xml_huge_tree=True)

    client = Client(WSDL_URL, settings=settings, transport=transport, plugins=[MyLoggingPlugin(),history])

    service = client.create_service("{urn:cisco:epas:soap}EpasSoapServiceBinding", SERVER_URL)

# First, you must log in with an application user.
# You would set 'force' to 'true' if you want to make sure you get a brand new session-key
# Set it to 'false' to keep re-using a session key you retrieved in a previous request

# We're using zeep to login, because the zeep library makes SOAP APIs easy

    login_admin = {
        'client-type': 'thirdpartyapp',
        'force': 'false',
        'username': AUSERNAME,
        'password': APASSWD
    }

    try:
    	resp = service.login(**login_admin)
    except Fault as err:
    	print("Zeep error: {0}".format(err))
    else:
        print("\n\n")
        print("\nSession Key:\n")
        print(resp.success['session-key'])
# get the admin user's session key, which we need to fetch an end user's session-key
        akey = resp.success['session-key']
        print("\n\n")
        print(history.last_sent)
        print(history.last_received)

# Now use the app user's session key to log in the end user.  You do not need the
# end user's password, just the app user's session-key.
# You would set 'force' to 'true' if you want to make sure you get a brand new session-key
# Set it to 'false' to keep re-using a session key you retrieved in a previous request

    login_euser = {
        'force': 'false',
        'client-type': 'thirdclient',
        'username': EUSERNAME,
        'app-session-id': akey
    }

    try:
    	resp = service.login(**login_euser)
    except Fault as err:
    	print("Zeep error: {0}".format(err))
    else:
        print("\n\n")
        print("\nSession Key:\n")
        print(resp.success['session-key'])
# get the end user's session key, which we need to do things like add-contact or delete-contact
        ekey = resp.success['session-key']
        print("\n\n")
        print(history.last_sent)
        print(history.last_received)


    with open('contacts.list','rb') as fh:
        contacts = json.load(fh)


# Read in the list of contacts we want to add or delete
# Wrap them in the XML tag, which specifies the domain

    chgcontacts=[]
    length=len(contacts)
    for i in range(length):
        chgcontacts.append('<urn:persona-id domain="'+SERVER+'">'+contacts[i]+'</urn:persona-id>')

# Add the contacts

# The default group is hard coded in the XML as "Contacts".
# If you want a different group, you need to change the XML below <urn:group name="Contacts">
# to reflect the name of the group you want

# Python rejects methods and variable names with hyphens (like "add-contact" and "session-key")
# because Python only recognizes the hyphen as a subtraction operation

# Rather than use painful workarounds in order to make zeep work with hyphenated methods,
# we bypass Zeep for this and use the requests library instead to send XML directly

    header={'content-type':'text/xml'}
    body = """
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:cisco:epas:soap">
           <soap:Header>
              <urn:session-key>"""+ekey+"""</urn:session-key>
           </soap:Header>
           <soap:Body>
              <urn:add-contact>
                 <urn:group name="Contacts">"""

    for i in range(length):
        body = body+chgcontacts[i]

    body = body + """
                 </urn:group>
              </urn:add-contact>
           </soap:Body>
        </soap:Envelope>
    """

    resp = requests.post(WSDL_URL,data=body,headers=header,verify=False)
