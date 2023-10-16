import json
from decimal import Decimal

with open('data_preprocessed.json','r') as f:
  reader=json.load(f,parse_float=Decimal)
  restaurants = list(reader)


fw = open('data_es_upload.txt','a')
ok = ''''''
for restaurant in restaurants:
    # print(restaurant['id'], restaurant['cusine'])
    indexx = { "index" : { "_index": "id", "_id" : restaurant['id'] } }
    index_data = {
        'cusine': restaurant['cusine']
    }
    ok+=(str(indexx))
    ok+=('\n')
    ok+=(str(index_data))
    ok+=('\n')

fw.write(ok)

# convert text to jsaon replace ' with " and hit run
    #  curl -XPOST -u 'opensearch:!Opensearch1' "https://search-restaurants-scc64pmmoarbfenp6oxckdrz3u.us-east-1.es.amazonaws.com/_bulk?pretty" --data-binary @1data_es_upload.json -H 'Content-Type: application/json'