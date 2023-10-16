import boto3
import json

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/061303142345/suggestionsQueue'

def lambda_handler(event, context):
    current_intent = event['currentIntent']
    if current_intent['name'] == 'greetingIntent':
        return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Hi there, how can I help?'
                    }
                }
            }
    elif current_intent['name'] == 'DiningSuggestionsIntent':
        slots = current_intent['slots']
    
        missing_slots = []
        for slot_name, slot_value in slots.items():
            if not slot_value:
                missing_slots.append(slot_name)
        
        if slots['cuisine'] is not None and slots['cuisine'].lower() not in ['indian', 'japanese', 'italian']:
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': current_intent['name'],
                    'slots': slots,
                    'slotToElicit': 'cuisine',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Please choose a valid cuisine: Indian, Japanese, or Italian.'
                    }
                }
            }
        
        if  slots['location'] is not None and slots['location'].lower() not in ['manhattan', 'new york']:
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': current_intent['name'],
                    'slots': slots,
                    'slotToElicit': 'location',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Please choose a valid location: Manhattan or New York.'
                    }
                }
            }
    
        if missing_slots:
            message = ''
            if missing_slots[0] == 'cuisine':
                message = 'Which cuisine do you prefer'
            elif missing_slots[0] == 'location':
                message = 'Which location are you looking for'
            elif missing_slots[0] == 'time':
                message = 'What time are you looking a table?'
            elif missing_slots[0] == 'num_people':
                message = 'How many people are there?'
            elif missing_slots[0] == 'email':
                message = 'Can you provide me your email so I can provide the recommendations'
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': current_intent['name'],
                    'slots': slots,
                    'slotToElicit': missing_slots[0],
                    'message': {
                        'contentType': 'PlainText',
                        'content': message
                    }
                }
            }
        
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            DelaySeconds=0,
            MessageAttributes={
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': slots['cuisine']
                },
                'location': {
                    'DataType': 'String',
                    'StringValue': slots['location']
                },
                'email': {
                    'DataType': 'String',
                    'StringValue': slots['email']
                },
                'time': {
                    'DataType': 'String',
                    'StringValue': slots['time']
                },
                'num_people': {
                    'DataType': 'Number',
                    'StringValue': slots['num_people']
                }
            },
            MessageBody='Restaurant Queries'
        )
        
    
        if response is not None:
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message': {
                        'contentType': 'PlainText',
                        'content': f'I will send an email to {slots["email"]} with recommendations for {slots["cuisine"]} restaurants'
                    }
                }
            }
        else:
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Failed',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Sorry there is an issue in generating the recommendations, Please try again later.'
                    }
                }
            }
    elif current_intent['name'] == 'ThankYouIntent':
        return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Thank You!!'
                    }
                }
            }

