# Cisco IM&P SOAP and REST examples

## A TALE OF TWO SERVICES

These scripts employ two different Cisco IM&P services. One is `EPASSoap`,
obviously a SOAP API.  The other is `PWS`, for which you can use SOAP or REST.
The examples here use REST for `PWS`.

You can download the documentation from here:
(https://developer.cisco.com/site/im-and-presence/documents/presence_web_service/latest_version/)

## THE EPASSoap SCRIPTS

## `addcontacts.py` and `delcontacts.py`

These are self-explanatory optional scripts for adding and deleting contacts
for the end user.  If you already have users and contacts set up to work with,
you won't need these scripts.

The API requests to add and delete contacts are only available as SOAP
requests.  So `addcontacts.py` and `delcontacts.py` both use EPASSoap,
not REST.

## THE PWS SCRIPTS

The API to set up your own presence notification handler is `PWS` or
`Presence Web Services`.  You can use SOAP or REST here, but REST is a
simpler API to work with, so our examples use REST, `pws-create.py`,
`pws-delete.py`, `endpoint.py` and (optional) `setpresence.py`.

The REST API procedure is generally as follows:

1. Log in an application user with the username and password.
This returns the app user session key

2. Use the app user session key to log in an end user with the end
user username, which returns an end user session key

3. Use the session keys to access the API requests you want.

## `pws-create.py`

1. Log in the application user and end user.

2. Use the app user session key to specify an endpoint URL.  This URL
points to the web service that will receive presence notifications.

3. Use the end user session key to subscribe for presence notifications
of a list of specified contacts.  When the presence for one of these
contacts changes, it will trigger a notification sent to the endpoint.
It is the responsibility of the web service endpoint to fetch the
actual presence status, whether it's BASIC presence or RICH presence.

## `pws-delete.py`

This script is simply an "undo" for `pws-create.py`.  It unsubscribes
presence notifications for the contacts and unregisters the endpoint URL.

Use this script to clear the subscriptions and endpoint when you want
to change anything and try again.

## `endpoint.py`

This is the web service that listens on port 5000 for REST-initiated
notifications that a contact's presence has changed.  It responds by
using a REST request to fetch the BASIC presence for that contact,
and appends the presence status response to the file `status.txt`.

## `setpresence.py`

This project works fine without this script if you want to change
the presence of a contact using any XMPP/Jabber client.  
If you don't want to use an XMPP/Jabber client, you can use this script
to change the presence of the contact defined in `enduser.json`.

Usage:

`python setpresence.py <one of AVAILABLE, BUSY, DND, AWAY, UNAVAILABLE or VACATION>`


## HOW TO PREPARE TO USE THE SCRIPTS

### INSTALL PYTHON

Install Python 3.7.  Follow the instructions for your OS from here:
(https://docs.python.org/3.7/using/index.html)

On Windows, choose the option to add to PATH environment variable

While we use the commands `pip` and `python` in this documentation,
you may need to substitute them with `pip3` and possibly `python3` on
Linux or Mac.

### CREATE A VIRTUAL ENVIRONMENT

It is good practice to create and work with a virtual environment.  This
lets you install a number of Python libraries needed only for your test
project, and not necessarily installed in your default Python setup.
See this link for instructions on how to set up a virtual environment
for your operating system: (https://docs.python.org/3/tutorial/venv.html)

Follow the instructions for entering your virtual environment, and then
proceed to install the necessary Python library dependencies for this
project.

Once you have your virtual environment installed, execute the correct
`activate` procedure for your OS so that you're operating from within
the virtual environment.

### INSTALL PYTHON DEPENDENCIES

The commands you'll need to install dependencies will vary from OS to OS.
Start with

    $ pip install zeep

This should automatically install most libraries you'll need. If you get
a message when you run a script that says your `import` doesn't work,
then try to `pip install <that dependency>`.  

Script Dependencies:
    `lxml`
    `requests`
    `zeep`
    `json`

The `endpoint.py` script needs `flask`, so run:

    $ pip install flask

### SET YOUR PARAMETERS

1. **[REQUIRED]** Edit `serverparams.json` to point to your Cisco IM&P
server and the administrator username and password credentials.  

The file also contains the host IP for the endpoint URL.  This is the
URL for the web service that listens for presence notifications.

The default port for the web service is 5000, so you'll need to make
sure the PC or server running `endpoint.py` can accept TCP traffic
over port 5000.  

```
{
  "params" : [
      {
        "SERVER" : "<your cimp server>",
        "USERNAME" : "administrator",
        "PASSWD" : "password"
        "HOST": "<host IP of the ENDPOINTURL>"
      }
  ]
}
```

2. **[REQUIRED]** Edit `appuser.json` to include the username and password
of your application user.  

```
{
  "params" : [
      {
        "USERNAME" : "<Application user name>",
        "PASSWD" : "<Application user password>"
      }
  ]
}
```

3. **[REQUIRED]** Edit `enduser.json` to include the username of the user whose
contacts you want to add, and the name of one of that user's contacts.

You want to specify only the user names, not the full JIDs.  In other words,
you want `joe` not `joe@somedomain.com`.  

The `USERNAME` is the name of the end user whose contact's presence you want
to monitor.

The `CONTACT` is the name of the user whose presence you want to monitor.

This data is used by the Presence Web Services (PWS) scripts
`pws-create.py`, `pws-delete.py`, `setpresence.py` and `endpoint.py`.

```
{
  "params" : [
      {
        "USERNAME" : "<Jabber end user name>",
        "CONTACT" : "<End user contact name you want to monitor for presence>"
      }
  ]
}
```

4. **[OPTIONAL]** Edit `contacts.list` to include contacts for your end user.

If the contact you specified for your end user already exists in
the end user's "buddy list" or "contacts" (or however your client
refers to contacts), you won't need to use `addcontacts.py`.  

In case you don't already have contacts for your test user, edit
`contacts.list` to include the names of one or more contacts you want
to add (or delete later) with `addcontacts.py` and `delcontacts.py`.

Make sure one of these contacts is the `CONTACT` you specified in
`enduser.json` (see above).

For example, if you specified `carlotta` as your `CONTACT`, you'll want
`carlotta` in the list:

```
[ "carlotta", "reed", "joe" ]
```

All contacts go into a group called `Contacts`.  This is hard coded
in the scripts, so you'd have to change the scripts to change that
group to another group name.  This shouldn't be necessary for the
scripts to work.  

If you're using the contacts only for testing purposes, you can remove
them when you're done with the script `delcontacts.py`.
