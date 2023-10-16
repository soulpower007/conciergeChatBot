import json
import boto3
import datetime
def lambda_handler(event, context):
    messages = event['messages']
    chatbotResponse = ""
    try:
        if len(messages) > 0:
            for message in messages:
                messageText = message['unstructured']['text']
                client = boto3.client('lex-runtime')
                lexResponse = client.post_text(botName='chatbot_two', botAlias='alias_two', userId='test', inputText=messageText)
                chatbotResponse = lexResponse['message']
    except Exception as e:
        print(e)
        chatbotResponse = "Please Try again!"
        
    response = {
        'messages': [
            {
                "type":"string",
                "unstructured": {
                    "id":"1",
                    "text": chatbotResponse,
                    "timestamp": str(datetime.datetime.now().timestamp())
                }
            }
        ]
    }
    
    return response
