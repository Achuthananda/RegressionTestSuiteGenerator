from akamaiproperty import AkamaiProperty
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urlparse
import pandas
import re
from atccondition import ATCCondition
import os
import getpass
username = getpass.getuser()
edgercpath = os.path.join("/", "Users", username,".edgerc")


edgerc = EdgeRc(edgercpath)
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

headers = {'Content-Type': 'application/json'}


atcCondition = ''


def createRegressionSuite(accountSwitchKey,config):
    testsuite = {}
    testsuite['testSuiteName'] = 'Regression Suite for {config}'.format(config=config)
    testsuite['testSuiteDescription'] = 'Auto Generated Regression Suite for {config}'.format(config=config)
    testsuite['locked'] = False
    testsuite['stateful'] = False

    testsuiteJson=json.dumps(testsuite)
    response = s.post(baseurl + ("/test-management/v2/functional/test-suites?accountSwitchKey=" + accountSwitchKey), data = testsuiteJson, headers = {'Content-Type':'application/json'})
    print(response)
    print(response.text)
    tests=json.loads(response.text)
    if response.status_code == 400:
        if tests['errors'][0]['type'] == 'entity.already.exists':
            print("Already Test Suite Exists")
            return str(tests['errors'][0]['existingEntities'][0]['testSuiteId'])
    else:
        testSuiteID = tests['testSuiteId']
        print("Test Suite ID:",testSuiteID)
        return testSuiteID

def createTestRequest(accountSwitchKey,fullurl):
    testrequest=[{"testRequestUrl": fullurl,"tags": ["testAPI"],"requestHeaders": []}]
    testjson=json.dumps(testrequest)
    atcrequest = s.post(baseurl + ("/test-management/v2/functional/test-requests?accountSwitchKey=" + accountSwitchKey), data = testjson, headers = {'Content-Type':'application/json'})
    print(atcrequest.status_code)
    body = json.loads(atcrequest.text)
    print(body)
    if len(body['failures']) != 0:
        print("Already Existing")
        return str(body['failures'][0]['existingEntities'][0]['testRequestId'])
    # error check
    reqid = ''
    reqid_success=(body['successes'])
    if reqid_success !=[]:
    	reqids=(body['successes'][0]['testRequestId'])
    	reqid=str(reqids)
    else:
    	reqid_failure=(body['failures'][0]['title'])
    	print("Test Request Failed..! Reason: " + reqid_failure)
    return reqid


def createTestCase(accountSwitchKey,requestId,conditionId,clientProfile):
    testCase=[{"testRequestId": requestId, "conditionId": conditionId,"clientProfileId": clientProfile}]

    testCaseJson=json.dumps(testCase)
    create_testcase = s.post(baseurl + ("/test-management/v2/functional/test-cases?accountSwitchKey=" + accountSwitchKey), data = testCaseJson, headers = {'Content-Type':'application/json'})
    body = json.loads(create_testcase.text)
    print(body)
    if create_testcase.status_code == 207:
        if len(body['failures']) != 0:
            testCaseId = str(body['failures'][0]['existingEntities'][0]['testCaseId'])
        else:
            print("Sepcial case")
            testCaseId = str(body['successes'][0]['testCaseId'])
        return testCaseId
    else:
        testCaseId=str(body['successes'][0]['testCaseId'])
        return testCaseId

def getConditionJson(atcCondition,conditions):
    conditionjson = {}
    if conditions["subject"] == "cpCode":
        conditionjson = atcCondition.cpcode(conditions["is"])
    elif conditions["subject"] == "tieredDistribution":
        conditionjson = atcCondition.tieredDistribution(conditions['enabled'])
    elif conditions["subject"] == "sureRoute":
        conditionjson = atcCondition.sureroute(conditions['enabled'])
    elif conditions["subject"] == "responseheader":
        if conditions["hasvalue"] == 'true':
            conditionjson = atcCondition.responseHeaderEquals(conditions['value'],conditions['equals'])
    elif conditions["subject"] == "caching":
        if conditions['option']  == 'cache':
            conditionjson = atcCondition.cache(conditions['option'],conditions['ttl'])
        else:
            conditionjson = atcCondition.cache(conditions['option'])
    return conditionjson

def atcCreator(accountSwitchKey,requestObject,config):
    atcCondition = ATCCondition('/Users/apadmana/.edgerc',accountSwitchKey)
    testrequestList = {}
    testcaseList = []
    for request in requestObject:
        fullurl = request[0]["RequestUrl"]
        print(fullurl)
        reqId = createTestRequest(accountSwitchKey,fullurl)
        testrequestList[reqId] = []
        conditionIdList = []
        for conditions in request[1:]:
            conditionjson = getConditionJson(atcCondition,conditions)
            condId = atcCondition.createCondition(conditionjson)
            conditionIdList.append(condId)
        testrequestList[reqId] = conditionIdList
        print('-----------------------------------------')
    print(testrequestList)
    for reqId in testrequestList:
        for conditionId in testrequestList[reqId]:
            print(reqId,conditionId)
            ipv4TestCaseId = createTestCase(accountSwitchKey,reqId,conditionId,1)
            ipv6TestCaseId = createTestCase(accountSwitchKey,reqId,conditionId,2)
            testcaseList.append(ipv4TestCaseId)
            #testcaseList.append(ipv6TestCaseId)
    print(testcaseList)
    regessionSuiteId = createRegressionSuite(accountSwitchKey,config)

    suiteId= [regessionSuiteId]
    suiteIdJson = json.dumps(suiteId)

    for testCase in testcaseList:
        testCaseAssignment = s.post(baseurl + ("/test-management/v2/functional/test-cases/"+ testCase + "/associations/test-suites/associate?accountSwitchKey=" + accountSwitchKey), data = suiteIdJson, headers = {'Content-Type':'application/json'})
        print(testCaseAssignment.status_code)
        if testCaseAssignment.status_code == 200:
            testCaseAssignmentJson=json.loads(testCaseAssignment.text)
            print("TestCase to testSuite assignment"  +  "\n" + str(testCaseAssignmentJson))
        else:
            print('Status Code:',testCaseAssignment.status_code)
            print('Body:',testCaseAssignment.text)
