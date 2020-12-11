import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import json
import re
import sys

edgerc = EdgeRc('/Users/apadmana/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

headers = {'Content-Type': 'application/json'}


def getSwitchKey(accountName):
    print("In get SwitchKey")
    id= accountName
    # Request switchkey for the Account name
    switchkey = s.get(baseurl + "/identity-management/v1/open-identities/u6r37xrz6fvk54mc/account-switch-keys?search="+id)
    # get the json in dictionary
    switchkey = json.loads(switchkey.text)
    # search for account switch key in the List and assign it to variable skey
    skey = (switchkey[0]['accountSwitchKey'])
    return skey
    #print("SwitchKey: " + skey)
