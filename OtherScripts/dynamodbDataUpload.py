# reference: https://gist.github.com/ngnmtl/6132ee83ccbe442994942700d8f8091b
access_key = 'AKIAURO4GNRE42XNXB4O' 

secret_access_key = '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'

import boto3
from decimal import Decimal
from datetime import datetime

import json
print(datetime.now())

session=boto3.Session(aws_access_key_id=access_key,aws_secret_access_key=secret_access_key, region_name='us-east-1')
client_dynamo=session.resource('dynamodb')
table=client_dynamo.Table('restaurant_cusine')
records=""
with open('data_preprocessed.json','r') as datafile:
  records=json.load(datafile,parse_float=Decimal)
count=0
print("forloop")
for i in records:
  i["insertedAtTimestamp"] = datatime.now()
  response=table.put_item(Item=i)
  count+=1
  print(count)