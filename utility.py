
import json
import requests
import calendar
import time
from datetime import datetime
from tqdm import tqdm


# -------- UTILITY FUNCTIONS -------------------
# Convert epoch to something readable (GMT)


def readable_time_gmt(timestamp):
    return time.strftime("%Y-%m-%d_%H:%M", time.gmtime(timestamp/1000))


def epoch_time(year, month, day, hour, minute, second):
    return calendar.timegm((year, month, day, hour, minute, second))*1000

# Get all timestamps in a given index (Recursive)


def get_timestamps_from_index(host, index, excludeList={}):
    header = {'Content-Type': 'application/json'}
    if len(excludeList) == 0:
        query = "{\"query\":{\"bool\":{\"must\":[{\"match_all\":{}}],\"must_not\":[],\"should\":[]}}}"
    else:
        must_not = ''
        for epoch in excludeList.keys():
            must_not += "{\"term\":{\"bucketTimestamp\":"+str(epoch)+"}},"

        query = "{\"query\":{\"bool\":{\"must\":[],\"must_not\":[<<SWAP>>],\"should\":[]}}}"
        query = query.replace("<<SWAP>>", must_not[:-1])
    try:
        response = requests.get(
            'http://'+host+':9200/'+index + '/_search', data=query, headers=header)
        response_obj = json.loads(response.text)
        print("TOTAL MATCHES: "+str(response_obj['hits']['total']))

        # Exit condition
        if response_obj['hits']['total'] == 0:
            return excludeList

        for hit in response_obj['hits']['hits']:
            t = hit['_source']['bucketTimestamp']
            if t in excludeList:
                excludeList[t] += 1
            else:
                excludeList.update({t: 1})

        # Recursion
        return get_timestamps_from_index(host, index, excludeList)
    except requests.exceptions.RequestException as e:
        print(e)

# Get all indexes that are contained for a given timestamp


def get_index_from_timestamp(host, dataset, interval, timestamp, excludeList={}):
    header = {'Content-Type': 'application/json'}
    if len(excludeList) == 0:
        query = "{\"query\":{\"bool\":{\"must\":[{\"term\":{\"timestamp\":"+str(
            timestamp)+"}}],\"must_not\":[],\"should\":[]}}}"
    else:
        must_not = ''
        for i in excludeList.keys():
            must_not += "{\"term\":{\"_index\":\""+i+"\"}},"
        query = "{\"query\":{\"bool\":{\"must\":[{\"term\":{\"timestamp\":"+str(
            timestamp)+"}}],\"must_not\":[<<SWAP>>],\"should\":[]}}}"
        query = query.replace("<<SWAP>>", must_not[:-1])
    try:
        response = requests.get('http://'+host+':9200/read_'+dataset +
                                '_'+str(interval)+'/_search', data=query, headers=header)
        response_obj = json.loads(response.text)
        print("TOTAL MATCHES: "+str(response_obj['hits']['total']))

        # Exit condition
        if response_obj['hits']['total'] == 0:
            sortedList = sorted(excludeList.items(),
                                key=lambda k: k[1], reverse=True)
            # for i in range(1, len(sortedList)):
            #     sortedList[i] = sortedList[i-1]-sortedList[i]
            return sortedList

        for hit in response_obj['hits']['hits']:
            index = hit['_index']
            if index not in excludeList:
                excludeList.update({index: response_obj['hits']['total']})
        return get_index_from_timestamp(host, dataset, interval, timestamp, excludeList)
    except requests.exceptions.RequestException as e:
        print(e)

# Read json file and output given property


def change_json_file(filename, propery):
    with open(filename) as f:
        data = json.load(f)

    for index in data['elasticsearch']:
        if "HOUR" in index['timeSpans']:
            print(index['dataset'])

    items = []
    for i in data.keys():
        items.append(i.encode('ascii', 'ignore'))

    items.sort()
    for i in items:
        print(i)


def parse_name_from_index(name):
    base = name.split("-")
    parts = base[0].split("_")
    return "_".join(parts[:-1])


def parse_interval_from_index(name):
    base = name.split("-")
    parts = base[0].split("_")
    return parts[-1]


def requeryIndexDiffCounts(timestamp, dataset, interval):
    print("RUNNING FOR: "+str(timestamp)+"  "+readable_time_gmt(timestamp))
    if dataset == None:
        response = requests.get(
            'https://datacopy-monitor-v1-unexpected-kudu.g3.app.cloud.comcast.net/force/'+str(interval)+'/'+str(timestamp))
    else:
        response = requests.get(
            'https://datacopy-monitor-v1-unexpected-kudu.g3.app.cloud.comcast.net/force/'+dataset+'/'+str(interval)+'/'+str(timestamp))
    print(response.status_code)
    print(response.text)
# ---------------------------- COPY INDEX FROM ONE ES CLUSTER TO ANOTHER -------------------------


def queryES(host, index, query):
    header = {'Content-Type': 'application/json'}
    url = 'http://'+host+':9200/'+index+'/_search'
    try:
        response = requests.get(url, data=query, headers=header)
        response_obj = json.loads(response.text)
        return response_obj
    except requests.exceptions.RequestException as e:
        print(e)


def saveES(host, index, data_type, query, ID):
    header = {'Content-Type': 'application/json'}
    # print("COPYING: "+str(ID))
    url = 'http://'+host+':9200/'+index+'/'+data_type+'/'+str(ID)
    # print("TO LOCATION: "+url)
    try:
        response = requests.put(url, data=query, headers=header)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(e)


def buildQuery(timestamp):
    response_size = 10000
    # return json.dumps({"query":{"bool":{"must":[{"term":{"bucketTimestamp":timestamp}}],"must_not":[],"should":[]}},"from":0,"size":response_size,"sort":[],"aggs":{}})
    return json.dumps({"query": {"bool": {"must": [{"match_all": {}}], "must_not": [], "should": []}}, "from": 0, "size": response_size, "sort": [], "aggs": {}})


def writeResponse(hits, target_host, target_index, target_data_type):
    for hitNum in tqdm(range(len(hits)), desc="Writing to elastic - "+target_index+": ", ncols=100):
        ID = hits[hitNum]['_id']
        data = hits[hitNum]['_source']
        # OPTIONAL: data.update({key:value})
        saveES(target_host, target_index,
               target_data_type, json.dumps(data), ID)


def checkClusterStatus(cluster):
    cluster_status = requests.get(
        'http://' + cluster + ':9200/_cluster/health?pretty=true')
    cluster_status_object = json.loads(cluster_status.text)

    while cluster_status_object['relocating_shards'] == 1:
        now = datetime.now()
        now_str = now.strftime("%d/%m/%Y %H:%M:%S")
        print(now_str+":  Still just a potato")
        time.sleep(10)
        cluster_status = requests.get(
            'http://' + cluster + ':9200/_cluster/health?pretty=true')
        cluster_status_object = json.loads(cluster_status.text)
    print("    No Longer A Potato!!!")

    print(cluster_status_object)

# ----------------------- ES ADD INDEX AND MAPPINGS ------------------

# header = {'Content-Type': 'application/json'}
# host = "localhost"
# index = "copy_list"
# index_type="copy_item"
# body = json.dumps({
#     "properties": {
#         "index": {
#             "type": "text",
#             "fields": {
#                 "keyword": {
#                     "ignore_above": 256,
#                     "type": "keyword"
#                 }
#             }
#         }
#     }
# })

# try:
#     response=requests.put('http://'+host+':9200/' +
#                             index, headers=header)
#     response = requests.put('http://'+host+':9200/' +
#                             index + '/'+index_type+'/_mapping', data=body, headers=header)
#     response_obj = json.loads(response.text)
#     print(response_obj)
# except requests.exceptions.RequestException as e:
#     print(e)

# ---------------------- ES RECORD OPERATIONS --------------------------
# header = {'Content-Type': 'application/json'}
# # host = "tvxels-hob-ct0002-g.mirs.aws.r53.xcal.tv"
# host="tvxels-le-ct10002-g.mirs.aws.r53.xcal.tv"
# # index = "media_tuning_60_copyto-99999"
# index="read_media_tuning_60"
# datatype = "MediaTuning"
# ID = "7VlWAGwBTyZwSDPH60GB"
# ids=["4FlWAGwBTyZwSDPH60GB",
# "6llWAGwBTyZwSDPH60GB",
# "7VlWAGwBTyZwSDPH60GB",

# "-7648394673679007999",
# "-8620881687418226489",
# "6598680545118867097"]
# query = json.dumps({
# "query":{"bool":{"must":[{"term": {"timestamp": "1563282000000"}}]}}, "size": 10000
# })
# query = json.dumps({
# "query":{"bool":{"must":[{"term": {"_id": ID}}]}}, "size": 10000
# })

# # UPDATE RECORD
# try:
#     response = requests.put('http://'+host+':9200/'+index +
#                             '/'+datatype+"/"+str(ID), data=query, headers=header)
#     response_obj = json.loads(response.text)
#     print(response_obj)
# except requests.exceptions.RequestException as e:
#     print(e)

# DELETE RECORD
# for ID in ids:
#     try:
#         response = requests.delete('http://'+host+':9200/'+index + '/'+datatype+"/"+str(ID), headers=header)
#         response_obj = json.loads(response.text)
#         print(response_obj)
#     except requests.exceptions.RequestException as e:
#         print(e)

# # GET RECORD
# try:
#     # response = requests.get('http://'+host+':9200/'+index + '/'+datatype+"/"+str(ID)+"?pretty=true", headers=header)
#     response = requests.get('http://'+host+':9200/'+index + '/_search?pretty=true', headers=header)
#     response_obj = json.loads(response.text)
#     times={}
#     for hit in response_obj['hits']['hits']:
#         print(hit['_source']['bucketTimestamp'])
#     # print(response.text)
# except requests.exceptions.RequestException as e:
#     print(e)

# GET RECORD BY QUERY
# try:
#     response = requests.get('http://'+host+':9200/'+index +'/_search', data=query, headers=header)
#     response_obj = json.loads(response.text)
#     print(response.text)
#     # print(response_obj['hits'])
#     # indexList={}
#     # for hit in response_obj['hits']['hits']:
#     #     if hit['_index'] in indexList:
#     #         indexList[hit['_index']]+=1
#     #     else:
#     #         indexList.update({hit['_index']:1})
#     # print(str(indexList))
# except requests.exceptions.RequestException as e:
#     print(e)


# # # ------------------- REQUERY INDEXES AT TIMESTAMP --------------------------
filename = '/Users/rwilk193/GitProjects/telemetry-data-service-config/index.json'
source_index = "smart_statistics_60-000361"
source_host = "tvxelc-le-ct10004-g.mirs.aws.r53.xcal.tv"
# source_host='tvxelc-hob-ct0005-g.mirs.aws.r53.xcal.tv'
# source_host="96.117.7.93"
# source_index="time_spent_watching_60_copyto-9999999"

# target_host="localhost"
# target_index="copy_list"
# target_data_type="copy_item"
year = 2019
month = 7
day = 23
hour = 8

timestamp = epoch_time(year, month, day, hour, 0, 0)
dataset = parse_name_from_index(source_index)
interval = parse_interval_from_index(source_index)

# # GET TIMESTAMPS IN AN INDEX
# timestamps=get_timestamps_from_index(source_host, source_index)
# print(source_index.upper())
# for t in sorted(timestamps.keys()):
#     print("  "+str(t)+"  "+readable_time_gmt(t))

# # GET INDEXES AT A TIMESTAMP
indexes=get_index_from_timestamp(source_host, dataset, interval, timestamp)
print(str(timestamp)+"  "+readable_time_gmt(timestamp)+"  "+source_host)
for i in indexes:
    print("  "+str(i))
print()

# CHECK HOST HEALTH
# checkClusterStatus(source_host)

# REQUERY INDEXES AT TIMESTAMP
# for i in range(0,13):
#     timestamp = epoch_time(year, month, day, hour+i, 0, 0)
#     requeryIndexDiffCounts(timestamp, dataset, interval)

# COPY DATA FROM ONE INDEX TO ANOTHER
# response=queryES(source_host, source_index, buildQuery(timestamp))
# copies=response['hits']['hits']
# writeResponse(copies, target_host, target_index, target_data_type)

# try:
#     response = requests.get(
#     "https://blog.bitsrc.io/the-principles-for-writing-awesome-angular-components-10e45f9ae77e")
#     text=response.text
#     start=text.find("<body>")
#     end=text.find("Resources")
#     print(text[start:end])
# except requests.exceptions.RequestException as e:
#     print(e)


# def fib(x):
#     a=1
#     b=0
#     temp=0

#     while(x>=0):
#         temp=a
#         a=a+b
#         b=temp
#         x=x-1
#     print(b)

# fib(499)


