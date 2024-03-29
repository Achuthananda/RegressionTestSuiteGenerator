from flask import Flask, escape, request
import requests
import sys
import os
sys.path.insert(1, 'utilities')
from switchkey import getSwitchKey
from config_parser import parseConfig,getHostnames
from url_fetcher import getBasePageUrls,getTopUrls
from atcinterface import atcCreator
from flask import Flask, render_template, escape, request
from request_qualifier import requestQualifier


global requestObject


requestObject = [
    [
        {
            "RequestUrl":"http://demohost2.edgesuite.net/akamaiflowershop/image/cache/WoodAnemone-120x120.jpg?dontcache=12"
        }
    ],
    [
        {
            "RequestUrl":"http://demohost1.edgesuite.net/css/style.css"
        }
    ],
    [
        {
            "RequestUrl":"http://demohost1.edgesuite.net/css/style.css?extendcache=True"
        }
    ]
]


global cpcodeList
global accountname
global config
global version
global accountSwitchKey
global hostNameList


cpcodeList = []
accountname = ''
config = ''
version = ''
accountSwitchKey = ''
hostNameList = []



app = Flask(__name__)
@app.route('/parseconfig')
def parseconfig():
    #Read Query String Parameters
    global accountname
    global config
    global version
    global cpcodeList
    global accountSwitchKey
    global hostNameList

    accountname = request.args.get('account_name')
    config = request.args.get('config_name')
    version = request.args.get('config_version')
    version = version[1:]

    #Get Account Switch key of the Account
    accountSwitchKey = getSwitchKey(accountname,config)
    behaviorParsedList = parseConfig(accountSwitchKey,config,version)
    hostNameList = getHostnames(accountSwitchKey,config,version)

    behaviorList = []

    for behavior in behaviorParsedList:
        behaviorList.append(behavior["behavior"]["name"])
        if behavior["behavior"]["name"] == 'cpCode':
            cpcodeList.append(behavior["behavior"]['options']['value']['id'])
    behaviorList = list(dict.fromkeys(behaviorList))

    return render_template('parse_results.html', behaviorList=behaviorList, hostNameList=hostNameList, accountname=accountname, configname=config, version=version)


@app.route('/createtest', methods=['POST'])
def createTest():
    print("In createtest")
    global config
    global version
    global accountSwitchKey
    global cpcodeList
    global requestObject
    global hostNameList

    urlsource = request.form['trigger-options']
    if urlsource == 'topurls':
        #requestObject = getTopUrls([951187],'AANA-1JHQYU')
        requestObject = getTopUrls(cpcodeList,accountSwitchKey)
    elif urlsource == 'allbasepageurls':
        requestObject = getBasePageUrls(hostNameList)
    else:
        templist = [urlsource]
        requestObject = getBasePageUrls(templist)

    requestObject = requestObject
    requestconditionObject = requestQualifier(config,version,requestObject)


    jsonfile = config+version+'.json'
    rmcommand = 'rm -rf ' + jsonfile
    os.system(rmcommand)

    atcCreator(accountSwitchKey,requestconditionObject,config)
    return render_template('testcreation.html')


if __name__ == '__main__':
    app.run()
