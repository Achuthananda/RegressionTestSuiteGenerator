from akamaiproperty import AkamaiProperty
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urlparse
import pandas
import re

headers = {'Content-Type': 'application/json'}




atc_behaviorlist = ["cpCode","cacheKeyQueryParams","caching","sureroute","tieredDistribution","responseCode","denyAccess",
                    "prefetch","gzipResponse","cacheKeyIgnoreCase"]

atc_behaviorlist = ["cpCode","caching","tieredDistribution","sureRoute","modifyOutgoingResponseHeader"]

headermapping = {}
headermapping["CONTENT_TYPE"] = "Content-Type"
headermapping["CACHE_CONTROL"] = "Cache-Control"
headermapping["PRAGMA"] = "Pragma"


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

def isSatisfy(criteriaSatisfy,urlObject,behavior):
    qsplist = urlObject.query.split('&')
    for eachCriteria in behavior["criteria"]:
        if not eachCriteria["criteria"]:
            continue
        if eachCriteria["condition"] == "all":
            satisfy = True
            for match in eachCriteria['criteria']:
                if match["name"] not in ["hostname","path","queryStringParameter"]:
                    satisfy = False
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
                if match["name"] not in ["hostname","path","queryStringParameter"]:
                    satisfy = False
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
    return criteriaSatisfy


def qualifyCPcode(urlObject,cpcodeCondition,behavior):
    cpcodeCondition["subject"] = "cpCode"
    #Default Rule
    if type(behavior["criteria"])  != list:
        cpcodeCondition["is"] = behavior["behavior"]["options"]["value"]["id"]
    else:#Not Default Rule
        criteriaSatisfy = True
        criteriaSatisfy = isSatisfy(criteriaSatisfy,urlObject,behavior)
        if criteriaSatisfy == True:
            cpcodeCondition["is"] = behavior["behavior"]["options"]["value"]["id"]



def qualifyCaching(urlObject,cacheCondition,behavior):
    cacheCondition["subject"] = "caching"
    #Default Rule
    if type(behavior["criteria"])  != list:
        if behavior["behavior"]["options"]["behavior"] == "MAX_AGE":
            cacheCondition["option"] = "cache"
            cacheCondition["ttl"] = behavior["behavior"]["options"]["ttl"]
        else:
            cacheCondition["option"] = behavior["behavior"]["options"]["behavior"]
    else:#Not Default Rule
        criteriaSatisfy = True
        criteriaSatisfy = isSatisfy(criteriaSatisfy,urlObject,behavior)
        if criteriaSatisfy == True:
            if behavior["behavior"]["options"]["behavior"] == "MAX_AGE":
                cacheCondition["option"] = "cache"
                cacheCondition["ttl"] = behavior["behavior"]["options"]["ttl"]
            else:
                cacheCondition["option"] = behavior["behavior"]["options"]["behavior"]


def qualifyTieredDistribution(urlObject,tdCondition,behavior):
    tdCondition["subject"] = "tieredDistribution"
    #Default Rule
    if type(behavior["criteria"])  != list:
        tdCondition["enabled"] = behavior["behavior"]["options"]["enabled"]
    else:#Not Default Rule
        criteriaSatisfy = True
        criteriaSatisfy = isSatisfy(criteriaSatisfy,urlObject,behavior)
        if criteriaSatisfy == True:
            tdCondition["enabled"] = behavior["behavior"]["options"]["enabled"]


def qualifySureRoute(urlObject,srCondition,behavior):
    srCondition["subject"] = "sureRoute"
    #Default Rule
    if type(behavior["criteria"])  != list:
        srCondition["enabled"] = behavior["behavior"]["options"]["enabled"]
    else:#Not Default Rule
        criteriaSatisfy = True
        criteriaSatisfy = isSatisfy(criteriaSatisfy,urlObject,behavior)
        if criteriaSatisfy == True:
            srCondition["enabled"] = behavior["behavior"]["options"]["enabled"]


def qualifyResponseHeader(urlObject,responseHeaderCondition,behavior):
    #print(behavior["criteria"])
    #print(behavior["behavior"])
    #Default Rule
    if type(behavior["criteria"])  != list:
        responseHeaderCondition["subject"] = "responseheader"
        if behavior["behavior"]["options"]["action"] == "DELETE":
            responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardDeleteHeaderName"]]
            responseHeaderCondition["exists"] = "false"

        elif behavior["behavior"]["options"]["action"] == "MODIFY":
            responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardModifyHeaderName"]]
            responseHeaderCondition["hasvalue"] = "true"
            responseHeaderCondition["equals"] = behavior["behavior"]["options"]["newHeaderValue"]

        elif  behavior["behavior"]["options"]["action"] == "ADD":
            responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardAddHeaderName"]]
            responseHeaderCondition["hasvalue"] = "true"
            responseHeaderCondition["equals"] = behavior["behavior"]["options"]["headerValue"]

    else:#Not Default Rule
        criteriaSatisfy = True
        criteriaSatisfy = isSatisfy(criteriaSatisfy,urlObject,behavior)
        #print(criteriaSatisfy)
        if criteriaSatisfy == True:
            responseHeaderCondition["subject"] = "responseheader"
            if behavior["behavior"]["options"]["action"] == "DELETE":
                responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardDeleteHeaderName"]]
                responseHeaderCondition["exists"] = "false"

            elif behavior["behavior"]["options"]["action"] == "MODIFY":
                responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardModifyHeaderName"]]
                responseHeaderCondition["hasvalue"] = "true"
                responseHeaderCondition["equals"] = behavior["behavior"]["options"]["newHeaderValue"]

            elif  behavior["behavior"]["options"]["action"] == "ADD":
                responseHeaderCondition["value"] = headermapping[behavior["behavior"]["options"]["standardAddHeaderName"]]
                responseHeaderCondition["hasvalue"] = "true"
                responseHeaderCondition["equals"] = behavior["behavior"]["options"]["headerValue"]



def requestQualifier(config,version,requestObject):
    jsonfile = config+version+'.json'
    fp = open(jsonfile,'r')
    behaviorlist = json.load(fp)

    for request in requestObject:
        fullurl = request[0]["RequestUrl"]
        urlObject = urlparse(fullurl)
        #print(fullurl)
        #print(urlObject.scheme)
        #print(urlObject.netloc)
        #print(urlObject.path)
        #print(urlObject.query)
        qsplist = urlObject.query.split('&')
        responseConditions = []
        cpcodeCondition = {}
        cacheCondition = {}
        tdCondition = {}
        srCondition = {}

        for behavior in behaviorlist:
            responseHeaderCondition = {}
            if behavior["behavior"]["name"] in atc_behaviorlist:
                if behavior["behavior"]["name"] == "cpCode":
                    qualifyCPcode(urlObject,cpcodeCondition,behavior)
                elif behavior["behavior"]["name"] == "caching":
                    qualifyCaching(urlObject,cacheCondition,behavior)
                elif behavior["behavior"]["name"] == "tieredDistribution":
                    qualifyTieredDistribution(urlObject,tdCondition,behavior)
                elif behavior["behavior"]["name"] == "sureRoute":
                    qualifySureRoute(urlObject,srCondition,behavior)
                elif behavior["behavior"]["name"] == "modifyOutgoingResponseHeader":
                    qualifyResponseHeader(urlObject,responseHeaderCondition,behavior)
                    if responseHeaderCondition:
                        responseConditions.append(responseHeaderCondition)

        request.append(cpcodeCondition)
        request.append(cacheCondition)
        request.append(tdCondition)
        request.append(srCondition)
        if responseConditions:
            for temp in responseConditions:
                request.append(temp)
    return requestObject

'''
request_object = [
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
requestObject = requestQualifier(request_object)
print(json.dumps(requestObject,indent=4))
'''
