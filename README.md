# Cisco IM&P SOAP and REST examples




Install Python 3.7

On Windows, choose the option to add to PATH environment variable

While we use `pip` and `python` in this project, you may need to substitute
them with `pip3` and possibly `python3` on Linux or Mac.

If this is a fresh installation, update pip

    $ python -m pip install --upgrade pip

It is advisable to create a virtual environment and work from that environment
instead of using your default Python installation.

Script Dependencies:
    `lxml`
    `requests`
    `zeep`
    `json`

Additional dependency for `endpoint.py`:
    `flask`

Dependency Installation:

    $ pip install zeep

On Windows, this will install automatically all of `zeep` dependencies,
including `lxml` and `requests`.

It may not install all dependencies on a platform other than Windows, so be aware
that you may need to `pip install` one or more dependencies individually.

For `endpoint.py`, run:

    $ pip install flask

IMPORTANT FILES:

1. Download AXL SQL Toolkit from CUCM.  Extract the desired version of the following
files into the working directory:  AXLAPI.wsdl, AXLEnums.xsd, AXLSoap.AXL_WSDL_URL

2. Edit serverparams.json to point to your Cisco IM&P server and the administrator
username and password credentials.  The file also contains the endpoint URL and
endpoint IP address (host), which is used for the presence notification code.
This information is not needed for deleting contacts, but the endpoint script
shares this file.

{
  "params" : [
      {
        "SERVER" : "<your cimp server>",
        "USERNAME" : "administrator",
        "PASSWD" : "password"
      }
  ]
}

3. Edit appuser.json to include the username and password of your application user.

{
  "params" : [
      {
        "USERNAME" : "<Application user name>",
        "PASSWD" : "<Application user password>"
      }
  ]
}

4. Edit enduser.json to include the username of the user whose contacts you want to add.

{
  "params" : [
      {
        "USERNAME" : "<Jabber end user name>",
        "CONTACT" : "<End user contact name you want to monitor for presence>"
      }
  ]
}

You'll also need to specify the username of a contact whose presence you want to
monitor for the Presence Web Services (PWS) scripts `pws-create.py`, `pws-delete.py`,
`setpresence.py` and `endpoint.py`. Set only the username, not the full JID
(ex. `joe` and not `joe@somedomain.com`)

5. Edit contacts.list to include the names of contacts you want to add or delete
with `addcontacts.py` and `delcontacts.py`.  

For example:

[ "carlotta", "reed", "rogue" ]
