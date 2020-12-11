from akamaiproperty import AkamaiProperty
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import pandas
import os
from datetime import datetime,timedelta
from time import strftime
import time


edgerc = EdgeRc('/Users/apadmana/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)


headers = {'Content-Type': 'application/json'}
def getStartDay(interval):
    start_day = 0
    if interval == 1:
        start_day = 29
    elif interval == 2:
        start_day = 59
    elif interval == 3:
        start_day = 89

    return start_day

def getBasePageUrls(hostnameList):
    print("Fetching basepage urls..")
    urllist = []
    for hostname in hostnameList:
        fullpath = 'http://'+hostname
        file_name = hostname + '.json'
        create_json_command = 'touch ' + file_name
        #print(create_json_command)
        os.system(create_json_command)
        lighthouse_command = 'lighthouse ' + fullpath + ' --quiet --output=json --output-path='+file_name
        #print(lighthouse_command)
        os.system(lighthouse_command)

        data = json.load(open(file_name))
        df = pandas.DataFrame(data["audits"]['network-requests']['details']['items'])
        filtered_df = df[df['url'].str.contains(fullpath)]
        filtered_df = filtered_df.drop(['startTime', 'transferSize','endTime','finished','resourceSize','resourceType'], axis = 1)

        urllist = urllist + filtered_df['url'].tolist()

        rmcommand = 'rm -rf ' + file_name
        os.system(rmcommand)

    requestObject = []
    for url in urllist:
        templist = []
        requrl = {}
        requrl["RequestUrl"] = url
        templist.append(requrl)
        requestObject.append(templist)
    return requestObject

def getTopUrls(cpCodeList,accountSwitchKey):
    print("Getting Top Urls..")
    urllist = []
    for cp_code in cpCodeList:
        data = {}
        data['objectIds'] = cp_code
        data["objectType"]=  "cpcode"
        data['metrics'] = ["allEdgeHits", "allOriginHits", "allHitsOffload"]

        json_data = json.dumps(data)
        interval = 1

        end = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).isoformat()
        start = (datetime.today()-timedelta(days=getStartDay(interval))).replace(hour=0,minute=0,second=0,microsecond=0).isoformat()

        params =    {
                        'accountSwitchKey': accountSwitchKey,
                        'start':start,
                        'end':end
                    }

        path = "reporting-api/v1/reports/urlhits-by-url/versions/1/report-data"
        fullurl = urljoin(baseurl, path)
        result = s.post(fullurl, headers=headers, data = json_data, params=params)
        code = result.status_code
        body = result.json()
        print(body)
        if code == 200:
            df=pandas.json_normalize(body['data'])
            pandas.set_option('display.max_rows', df.shape[0]+1)

            df['allEdgeHits'] = df['allEdgeHits'].astype(int)
            df['allOriginHits'] = df['allOriginHits'].astype(int)

            df.sort_values(by=['allEdgeHits'], inplace=True, ascending=False)
            newdf = df.head(5)
            print(newdf)
            urllist = urllist + newdf['hostname.url'].tolist()
        else:
        	print ("Failed to retrieve configuration details.")
        	print ("Response Code: ",code)

    print(urllist)
    requestObject = []
    for url in urllist:
        templist = []
        requrl = {}
        requrl["RequestUrl"] = url
        templist.append(requrl)
        requestObject.append(templist)
    return requestObject


'''
basepagedf = getBasePageURLs("www.tui.co.uk")
urlist = basepagedf['url'].tolist()
print(urlist)


topurls = getTopUrls([951187],'AANA-1JHQYU')
topurllist = topurls['hostname.url'].tolist()
print(topurllist)
'''
