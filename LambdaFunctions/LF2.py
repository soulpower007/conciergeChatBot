import json
import boto3
import decimal
import random
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import constants


#OpenSearch / Elastic Search query part
REGION = constants.REGION
HOST = 'search-restaurants-scc64pmmoarbfenp6oxckdrz3u.us-east-1.es.amazonaws.com'
INDEX = 'id'

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(constants.ACCESS,
                    constants.SECRET_ACCESS,
                    region,
                    service
                    )

def elasticquery(term):
    q = {'size': 100, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
        http_auth=get_awsauth(REGION, 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

    res = client.search(index='id', body=q)
    # print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        # results.append(hit['_source']['cusine'])
        results.append(hit['_id'])
        
    return results


def send_email(restaurants,email):
    try:
        client = boto3.client('ses')
        mailBody = "Hi here are 5 restaurants matching your preferences\n"
        for restaurant in restaurants:
            mailBody = mailBody + f'{restaurant["name"] } ' 
            mailBody = mailBody + f'{" ".join(restaurant["display_address"])}' + '\n'
        response = client.send_email(
            Source='aa11164@nyu.edu',
            Destination={
                'ToAddresses': [
                   email,
                ]},
                Message={
                'Subject' : {
                    'Data' : "Dining Concierge Restaurant Recommendations"
                },
                'Body' :{
                    'Text' :{
                       'Data' : str(mailBody)
                    }
                }
            }
        )
        print('email sent')
    except KeyError:
        logger.debug("Error sending ")



def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(0,len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    else:
        return obj

def get_dynamo_data(dynno, table, key):
    response = table.get_item(Key={'id':key}, TableName='yelp-restaurants')
    # print(response)
    response = replace_decimals(response)
    # print('abcd')
    # print(response)
    
    name = response['Item']['name'] if response['Item']['name'] else None
    rating = response['Item']['rating'] if response['Item']['rating'] else None
    display_address = response['Item']['location']['display_address'] if  response['Item']['location']['display_address'] else None
    # review_count = response['Item']['review_count'] if  response['Item']['review_count'] else None
    # coordinates = response['Item']['coordinates']  if response['Item']['coordinates']  else None
    
    return {"name":name,
            "rating": rating,
            # "price": price,
            "display_address":display_address,
            # "review_count": review_count,
            # "coordinates":coordinates
            } 


def lambda_handler(event=None, context=None):
    # TODO implement

    # Fetch Query from SQS
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/061303142345/suggestionsQueue'
    
    
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'time', 'cuisine', 'location', 'num_people', 'email'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    messages = response['Messages'] if 'Messages' in response.keys() else []
            
    while messages:
        message = messages.pop()
        msg_attributes=message['MessageAttributes']
        query = {"query": {"match": {"cuisine": msg_attributes["cuisine"]["StringValue"]}}}
        email = msg_attributes["email"]["StringValue"]
        chat_cusine =  msg_attributes["cuisine"]["StringValue"]

        # Fetch the IDS from elasticsearch
        ids = elasticquery(chat_cusine)
        restaurant_id_indices = random.sample(ids,5)

        # init dynamodb details
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('yelp-restaurants')
        
        restaurants_set = []

        # iterate through indices and get details     
        for id in restaurant_id_indices:
            suggested_restaurant = get_dynamo_data(dynamodb, table, id)
            restaurants_set.append(suggested_restaurant)
        
        send_email(restaurants_set,email)
    
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
    
    return {
        'statusCode': 200,
        'body': ''
    }

# lambda_handler()