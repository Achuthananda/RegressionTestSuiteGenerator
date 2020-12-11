from akamaiproperty import AkamaiProperty
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urlparse
import pandas
import re

headers = {'Content-Type': 'application/json'}


fp = open('../behaviors.json','r')
behaviorlist = json.load(fp)

atc_behaviorlist = ["cpCode","cacheKeyQueryParams","caching","sureroute","tieredDistribution","responseCode","denyAccess",
                    "prefetch","gzipResponse","cacheKeyIgnoreCase"]

atc_behaviorlist = ["cpCode"]


def getCriteriaType(criteriaObject):
    if criteriaObject["name"] == "hostname":
        return

def hostNameOneOf(hostname,hostlist):
    if hostname in hostlist:
        return True
    else:
        return False

def hostNameNotOneOf(hostname,hostlist):
    if hostname not in hostlist:
        return True
    else:
        return False

def pathMatches(path,pathList):
    val = False
    for eachpath in pathList:
        if re.match(eachpath, path):
            return True
    return val

def pathDoesntMatch(path,pathList):
    val = True
    for eachpath in pathList:
        if re.match(eachpath, path):
            return False
    return val

def qspOneOf(qspList,qspName,qspValue):
    val = False
    for qsp in qspList:
        if qsp.split('=')[0] == qspName:
            if qsp.split('=')[1] in qspValue:
                return True
    return val

def qspNotOneOf(qspList,qspName,qspValue):
    val = False
    for qsp in qspList:
        if qsp.split('=')[0] == qspName:
            if qsp.split('=')[1] not in qspValue:
                return True
    return val

def qspExists(qspList,qspName):
    val = False
    for qsp in qspList:
        if qsp.split('=')[0] == qspName:
            return True
    return val

def qspDoesntExist(qspList,qspName):
    val = False
    for qsp in qspList:
        if qsp.split('=')[0] != qspName:
            val = True
    return val


def requestQualifier(requestObject):
    for request in requestObject:
        fullurl = request["RequestUrl"]
        urlObject = urlparse(fullurl)
        print(fullurl)
        #print(urlObject.scheme)
        #print(urlObject.netloc)
        #print(urlObject.path)
        #print(urlObject.query)
        qsplist = urlObject.query.split('&')
        cpcodeCondition = {}
        for behavior in behaviorlist:
            if behavior["behavior"]["name"] in atc_behaviorlist:
                if behavior["behavior"]["name"] == "cpCode":
                    #print("-------------------------------------------------------------------------------")
                    #print(behavior["behavior"])
                    #print(behavior["criteria"])
                    cpcodeCondition["subject"] = "cpCode"

                    #Default Rule
                    if type(behavior["criteria"])  != list:
                        cpcodeCondition["is"] = behavior["behavior"]["options"]["value"]["id"]
                        #print(cpcodeCondition)
                    else:#Not Default Rule
                        criteriaSatisfy = True
                        for eachCriteria in behavior["criteria"][1:]:
                            if eachCriteria["condition"] == "all":
                                satisfy = True
                                for match in eachCriteria['criteria']:
                                    if match["name"] == "hostname":
                                        if match["options"]["matchOperator"] == "IS_ONE_OF":
                                            satisfy &= hostNameOneOf(urlObject.netloc,match["options"]["values"])
                                        else:
                                            satisfy &= hostNameNotOneOf(urlObject.netloc,match["options"]["values"])

                                    if match["name"] == "path":
                                        if match["options"]["matchOperator"] == "MATCHES_ONE_OF":
                                            satisfy &= pathMatches(urlObject.path,match["options"]["values"])
                                        else:
                                            satisfy &= pathDoesntMatch(urlObject.path,match["options"]["values"])

                                    if match["name"] == "queryStringParameter":
                                        if match["options"]["matchOperator"] == "IS_ONE_OF":
                                            satisfy &= qspOneOf(qsplist,match["options"]["parameterName"],match["options"]["values"])
                                        if match["options"]["matchOperator"] == "IS_NOT_ONE_OF":
                                            satisfy &= qspNotOneOf(qsplist,match["options"]["parameterName"],match["options"]["values"])
                                        if match["options"]["matchOperator"] == "EXISTS":
                                            satisfy &= qspExists(qsplist,match["options"]["parameterName"])
                                        if match["options"]["matchOperator"] == "DOES_NOT_EXIST":
                                            satisfy &= qspDoesntExist(qsplist,match["options"]["parameterName"])

                            else:
                                satisfy = False
                                for match in eachCriteria['criteria']:
                                    if match["name"] == "hostname":
                                        if match["options"]["matchOperator"] == "IS_ONE_OF":
                                            satisfy |= hostNameOneOf(urlObject.netloc,match["options"]["values"])
                                        else:
                                            satisfy |= hostNameNotOneOf(urlObject.netloc,match["options"]["values"])

                                    if match["name"] == "path":
                                        if match["options"]["matchOperator"] == "MATCHES_ONE_OF":
                                            satisfy |= pathMatches(urlObject.path,match["options"]["values"])
                                        else:
                                            satisfy |= pathDoesntMatch(urlObject.path,match["options"]["values"])

                                    if match["name"] == "queryStringParameter":
                                        if match["options"]["matchOperator"] == "IS_ONE_OF":
                                            satisfy |= qspOneOf(qsplist,match["options"]["parameterName"],match["options"]["values"])
                                        if match["options"]["matchOperator"] == "IS_NOT_ONE_OF":
                                            satisfy |= qspNotOneOf(qsplist,match["options"]["parameterName"],match["options"]["values"])
                                        if match["options"]["matchOperator"] == "EXISTS":
                                            satisfy |= qspExists(qsplist,match["options"]["parameterName"])
                                        if match["options"]["matchOperator"] == "DOES_NOT_EXIST":
                                            satisfy |= qspDoesntExist(qsplist,match["options"]["parameterName"])

                            criteriaSatisfy &= satisfy
                            #print("Criteria is :",criteriaSatisfy)
                            #print("---------------------------------")
                        if criteriaSatisfy == True:
                            cpcodeCondition["is"] = behavior["behavior"]["options"]["value"]["id"]
                            #print(cpcodeCondition)

        print(cpcodeCondition)










request_object = [
    {
        "RequestUrl":"http://achuth-autest.edgesuite.net/css/bootstrap.css",
        "RequestHeader": "Accept:Encoding",
        "RequestHeader": "Host:test.akamai.com"
    },
    {
        "RequestUrl":"http://achuth-autest.edgesuite.net/images/17.jpg",
        "RequestHeader": "Accept:Encoding",
        "RequestHeader": "Host:test.akamai.com"
    },
    {
        "RequestUrl":"http://achuth-autest.edgesuite.net/js/classie.js?test=123"
    }
]

request_object = [
    {
        "RequestUrl":"http://atc.edgesuite.net/js/classie.js"
    },
    {
        "RequestUrl":"http://atc.edgesuite.net/images/17.jpg"
    },
    {
        "RequestUrl":"http://atc.edgesuite.net/images11/17.jpg"
    },
    {
        "RequestUrl":"http://atc.edgesuite.net/images/17.jpg?qsptoken3=hello"
    },
    {
        "RequestUrl":"http://atc.edgesuite.net/css/bootstrap.css"
    },
    {
        "RequestUrl":"http://atctechjam.edgesuite.net/js/classie.js"
    },
    {
        "RequestUrl":"http://atctechjam.edgesuite.net/images/17.jpg"
    },
    {
        "RequestUrl":"http://atctechjam.edgesuite.net/images11/17.jpg"
    },
    {
        "RequestUrl":"http://atctechjam.edgesuite.net/images/17.jpg?qsptoken3=hello"
    },
    {
        "RequestUrl":"http://atctechjam.edgesuite.net/css/bootstrap.css"
    }
]
requestQualifier(request_object)
