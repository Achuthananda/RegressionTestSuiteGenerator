import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import json
import re
import sys
from akamaiproperty import AkamaiProperty
import os
import getpass

username = getpass.getuser()
edgercpath = os.path.join("/Users",username,".edgerc")

edgerc = EdgeRc(edgercpath)
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

headers = {'Content-Type': 'application/json'}


def getSwitchKey(accountName,config):
    print("In get SwitchKey")
    id= accountName
    # Request switchkey for the Account name
    switchkey = s.get(baseurl + "/identity-management/v1/open-identities/u6r37xrz6fvk54mc/account-switch-keys?search="+id)
    # get the json in dictionary
    switchkey = json.loads(switchkey.text)
    # search for account switch key in the List and assign it to variable skey
    skeylist = [x['accountSwitchKey'] for x in switchkey]

    for x in skeylist:
        pr = AkamaiProperty(edgercpath,config,x)
        if pr.getStagingVersion() != -1:
            return x
