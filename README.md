# Cisco IM&P SOAP and REST examples




Install Python 3.7

On Windows, choose the option to add to PATH environment variable

While we use the commands `pip` and `python` in this documentation,
you may need to substitute them with `pip3` and possibly `python3` on
Linux or Mac.

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

It may not install all dependencies on a platform other than Windows,
so be aware that you may need to `pip install` one or more dependencies
individually.

The `endpoint.py` script needs `flask`, so run:

    $ pip install flask

## SET YOUR PARAMETERS

1. Edit `serverparams.json` to point to your Cisco IM&P server and the
administrator username and password credentials.  

The file also contains the endpoint URL and endpoint IP address (host).
This information is not needed for all scripts, but the endpoint script
shares this file and needs to know the host.  The default port for
the web service is 5000, but you can change that within the script.
If you change the port, make sure you change `serverparams.json` to reflect
that change.

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

2. Edit `appuser.json` to include the username and password of your
application user.

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

3. Edit `enduser.json` to include the username of the user whose contacts
you want to add, and the name of one of that user's contacts. You want to
specify only the user names, not the full JIDs.  In other words, you want
`joe` not `joe@somedomain.com`.  The `CONTACT` name is used by
the Presence Web Services (PWS) scripts `pws-create.py`, `pws-delete.py`,
`setpresence.py` and `endpoint.py`.

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

4. In case you don't already have contacts for your test user, edit
contacts.list to include the names of one or more contacts you want
to add (or delete later) with `addcontacts.py` and `delcontacts.py`.
Make sure your end user has the `CONTACT` you specified in
`enduser.json`. If you need to add that contact, you can list it
here.  

For example:

```
[ "carlotta", "reed", "rogue" ]
```

All contacts go into a group called `Contacts`.  This is hard coded
in the scripts, so you'd have to change the scripts to change that
group to another group name.
