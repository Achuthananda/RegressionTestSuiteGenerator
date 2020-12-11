from flask import Flask, escape, request
import requests
import sys
import os
sys.path.insert(1, 'utilities')
from switchkey import getSwitchKey
from config_parser import parseConfig,getHostnames
from url_fetcher import getBasePageUrls,getTopUrls
from atcinterface import atcCreator
from request_qualifier import requestQualifier



requestObject = [
    [
        {
            "RequestUrl":"http://atc.edgesuite.net/js/classie.js"
        }
    ],
    [
        {
            "RequestUrl":"http://atc.edgesuite.net/images/17.jpg"
        }
    ],
    [
        {
            "RequestUrl":"http://atc.edgesuite.net/images/17.jpg?qsptoken=1223"
        }
    ],
    [
        {
            "RequestUrl":"http://atc.edgesuite.net/images/17.jpg?qsptoken3=hello"
        }
    ],
    [
        {
            "RequestUrl":"http://atc.edgesuite.net/css/bootstrap.css"
        }
    ],
    [
        {
            "RequestUrl":"http://atctechjam.edgesuite.net/js/classie.js"
        }
    ]
]

app = Flask(__name__)
@app.route('/parseconfig')
def parseconfig():
    #Read Query String Parameters
    accountname = request.args.get('account_name')
    config = request.args.get('config_name')
    version = request.args.get('config_version')
    version = version[1:]

    #Get Account Switch key of the Account
    accountSwitchKey = getSwitchKey(accountname)
    behaviorParsedList = parseConfig(accountSwitchKey,config,version)
    hostNameList = getHostnames(accountSwitchKey,config,version)

    behaviorList = []
    cpcodeList = []
    for behavior in behaviorParsedList:
        behaviorList.append(behavior["behavior"]["name"])
        if behavior["behavior"]["name"] == 'cpCode':
            cpcodeList.append(behavior["behavior"]['options']['value']['id'])
    behaviorList = list(dict.fromkeys(behaviorList))

    #print(behaviorList)
    #print(hostNameList)
    #print(cpcodeList)

    #requestObject = getTopUrls(cpcodeList,accountSwitchKey)
    #requestObject = getTopUrls([951187],'AANA-1JHQYU')
    templist = [hostNameList[1]]
    requestObject = getBasePageUrls(templist)
    print(requestObject)

    requestconditionObject = requestQualifier(config,version,requestObject)
    jsonfile = config+version+'.json'
    rmcommand = 'rm -rf ' + jsonfile
    os.system(rmcommand)

    #print("The req object is :",requestconditionObject)
    atcCreator(accountSwitchKey,requestconditionObject,config)

    return f'Hello, {escape(accountSwitchKey)}!'


if __name__ == '__main__':
    app.run()
