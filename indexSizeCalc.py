from datetime import datetime
import calendar
from tqdm import tqdm
import json
import requests
import time


# source_host = "tvxelc-le-ct10004-g.mirs.aws.r53.xcal.tv"
# source_host='tvxelc-hob-ct0005-g.mirs.aws.r53.xcal.tv'
source_host='tvxels-lw-ct00001-g.mirs.aws.r53.xcal.tv'

def readable_time_gmt(timestamp):
    return time.strftime("%Y-%m-%d_%H:%M", time.gmtime(timestamp/1000))

def epoch_time(year, month, day, hour, minute, second):
    return calendar.timegm((year, month, day, hour, minute, second))*1000

def getAllIndexes(cluster):
    cluster_indexes = requests.get(
        'http://' + cluster + ':9200/_cat/indices?v')
    return cluster_indexes.text

def parse_interval_from_index(name):
    base = name.split("-")
    parts = base[0].split("_")
    if parts[-1].isdigit():
        return parts[-1]
    elif parts[-1]=='copyto':
        if parts[-2].isdigit():
            return parts[-2]
    else:
        return 1

def convertToSize(size):
    num=float(size[0:-2])
    unit=size[-2]
    if unit=='k':
        num=num*1000
    elif unit=='m':
        num=num*1000000
    elif unit=='g':
        num=num*1000000000
    return num

def buildIndexItems(index_list_raw):
    index_list=[]
    lines=index_list_raw.split('\n')
    for i in range(1,len(lines)-1):
        item_raw=lines[i].split()
        interval = parse_interval_from_index(item_raw[2])
        item={'name':item_raw[2], 'size':convertToSize(item_raw[9]), 'interval':interval}
        index_list.append(item)
    return index_list

def getAverageDocSize(item, source_host):
    header = {'Content-Type': 'application/json'}
    query = "{\"query\":{\"bool\":{\"must\":[{\"match_all\":{}}],\"must_not\":[],\"should\":[]}}}"
    try:
        response = requests.get(
            'http://'+source_host+':9200/'+item['name'] + '/_search', data=query, headers=header)
        response_obj = json.loads(response.text)
        total=response_obj['hits']['total']
        item.update({'doc_count':total})
    except requests.exceptions.RequestException as e:
        print(e)

    if item['doc_count']>0:
        unitCount=item['size']/item['doc_count']
    else:
        unitCount=0
    item.update({'doc_size':unitCount})
    return item

def buildRangeQuery(start, end):
    return json.dumps({
    "query":{
        "range" : {
            "bucketTimestamp" : {
                "gte" : start,
                "lt" : end,
                "boost" : 2.0
            }
        }
    }, "size": 0
    })

def getDocsInLast24(item, source_host, start_timestamp, end_timestamp):
    header = {'Content-Type': 'application/json'}
    try:
        response = requests.get(
            'http://'+source_host+':9200/'+item['name'] + '/_search', data=buildRangeQuery(start_timestamp, end_timestamp), headers=header)
        response_obj = json.loads(response.text)
        match_total=response_obj['hits']['total']
    except requests.exceptions.RequestException as e:
        print(e)

    index.update({'matches':match_total, 'daily_size':match_total*index['doc_size']})
    return item

def aggregateCounts(item, running_sum={}):
    if item['matches']>0:
        if item['interval'] in sum:
            running_sum[item['interval']]+=item['daily_size']
        else:
            running_sum.update({item['interval']:item['daily_size']})
    return running_sum

print("----Checking "+source_host)
index_list_raw=getAllIndexes(source_host)
index_list=buildIndexItems(index_list_raw)

sum={}
ct = datetime.now() 
start = epoch_time(ct.year, ct.month, ct.day-1, ct.hour, ct.minute, 0)
end= epoch_time(ct.year, ct.month, ct.day, ct.hour, ct.minute, 0)
print("  Start Time: "+readable_time_gmt(start))
print("  End Time: "+readable_time_gmt(end))
for i in tqdm(range(len(index_list)), desc="Counting Things & Stuff: ", ncols=100):
    index=index_list[i]
    index=getAverageDocSize(index, source_host)
    index=getDocsInLast24(index, source_host, start, end)
    sum=aggregateCounts(index, sum)


sorted_index_list=sorted(index_list, key=lambda k: int(k['interval']))
for i in sorted_index_list:
    if i['matches']>0:
        print("{:40s}  {:10s}  {:10s}".format(i['name'],str(i['matches']/1000)+"k",str(i['daily_size']/1000000000)+"gb"))

print("---RESULTS---")
print(source_host)
total=0
for interval in sorted(sum, key=lambda k: int(k)):
    print("  "+str(interval)+": "+str(round(sum[interval]/1000000000, 2))+'gb')
    total+=sum[interval]

print("  TOTAL: "+str(round(total/1000000000, 2))+'gb')

