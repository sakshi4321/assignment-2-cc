import json
import boto3
import requests


AMAZON_LEX_BOT = "PhotoBot"
LEX_BOT_ALIAS = "versionfive"
USER_ID = "user"


TABLENAME = 'photo'
ELASTIC_SEARCH_URL = "https://search-photo-642lpewxbstxmttgvqhduxrhtm.us-east-1.es.amazonaws.com/_search?q="

S3_URL = "https://photobucketassign2.s3.amazonaws.com/"

def post_on_lex(query, user_id=USER_ID):
    """
    Get the user input from the frontend as text and pass
    it to lex. Lex will generate a new response.
    it will return a json response:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lex-runtime.html
    """
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(botName=AMAZON_LEX_BOT,
                                    botAlias=LEX_BOT_ALIAS,
                                    userId=user_id,
                                    inputText=query)

    if lex_response['slots']['userquery'] and lex_response['slots']['userquerytwo']:
        labels = 'labels:' + lex_response['slots']['userquery'] + '+' + 'labels:' + lex_response['slots']['userquerytwo']
    elif lex_response['slots']['userquery']:
        labels = 'labels:' + lex_response['slots']['userquery']
    else:
        return
    return labels


def get_photos_ids(URL, labels):
    """
    return photos ids having the
    labels as desired
    """

    URL = URL + str(labels)
    #response = requests.get(URL, auth=awsauth).content
    response = requests.get(URL, auth=("PhotoBK","PhotoBK@123")).content
    print("Response: ",response)
    data = json.loads(response)
    hits = data["hits"]["hits"]
    id_list = []
    labels_list = []
    for result in hits:
        _id = result["_source"]["objectKey"]
        id_list.append(_id)
        _labels = result["_source"]["labels"]
        labels_list.append(_labels)
    return id_list, labels_list


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin":"*",
            "Access-Control-Allow-Credentials" : True,
        },
    }

def lambda_handler(event, context):

    query = event['queryStringParameters']['q']
    #query = "Show me dog"
    labels = post_on_lex(query)
    id_list, labels_list = get_photos_ids(ELASTIC_SEARCH_URL, labels)

    results = []
    for i, l in zip(id_list, labels_list):
        results.append({"url": S3_URL + i, "labels": l})

    print(results)
    response = {"results": results}
    return respond(None, response)
    
    
    
    
# import math
# import dateutil.parser
# import datetime
# import time
# import os
# import logging
# import boto3
# import json
# import requests
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# # https://stackoverflow.com/questions/52358345/aws-lex-select-query-from-user-question
# """ --- Get PhotoId from elastic search--- """


# def elastic_search_id(label):
    
#     esUrl = 'https://search-photo-642lpewxbstxmttgvqhduxrhtm.us-east-1.es.amazonaws.com/_search?q='+label
#     print(esUrl)
#     response = requests.get(esUrl, auth=("PhotoBK", "PhotoBK@123")).content
    
#     data = json.loads(response)
#     print(data)
#     hits = data["hits"]["hits"]
#     id_list = []
#     labels_list = []
#     for result in hits:
#         _id = result["_source"]["objectKey"]
#         id_list.append(_id)
#         _labels = result["_source"]["labels"]
#         labels_list.append(_labels)
#     return id_list, labels_list

# """ --- Get keywords from message --- """


# # def get_keywords(response_string):

# #     char_remove = ["show", "me", "with", "photos", "the", "and", ","]
# #     # filter out the key words
# #     for i in char_remove :
# #         response_string = response_string.replace(i,"")
# #     word_list=list(response_string.split(" "))
# #     return word_list 


# def post_on_lex(query):
#     """
#     Get the user input from the frontend as text and pass
#     it to lex. Lex will generate a new response.
#     it will return a json response:
#     https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lex-runtime.html
#     """
#     client = boto3.client('lex-runtime')
#     lex_response = client.post_text(botName="PhotoBot",
#                                     botAlias="versionfive",
#                                     userId="User1",
#                                     inputText=query)
#     print(lex_response)
#     if lex_response['slots']['userquery'] and lex_response['slots']['userquerytwo']:
#         labels = 'labels:' + lex_response['slots']['userquery'] + '+' + 'labels:' + lex_response['slots']['userquerytwo']
#     elif lex_response['slots']['userquery']:
#         labels = 'labels:' + lex_response['slots']['userquery']
#     else:
#         return
#     return labels
    
# def lambda_handler(event, context):
   
#     # connect to lex
#     # client = boto3.client('lex-runtime')
#     # print("event is: ", event)
#     # user_id = 'user1'
#     # bot_name_lex = 'PhotoBot'
#     # bot_alias =  'versionfive'
#     # response = client.post_text(
#     # botName=bot_name_lex ,
#     # botAlias= bot_alias,
#     # userId=user_id,
#     # sessionAttributes={
#     #     'string': 'string'
#     # },
#     # requestAttributes={
#     #     'string': 'string'
#     # },
#     # inputText= msg_text
#     # ) 
#     # #Get message 
#     # msg_text = event['messages'][0]['unstructured']['text']
#     # #Get words 
#     # keywords = get_keywords(msg_text)
#     #query = event['queryStringParameters']['q']
#     query = "show me cat"
#     labels = post_on_lex(query)
#     body = {'Responses':[]}
    

    
#     id_list, labels_list = elastic_search_id(labels)
#     results = []
#     for i, l in zip(id_list, labels_list):
#         results.append({"url": S3_URL + i, "labels": l})
        
#     response = {"results": results}

#     print("test_001")
      
#     # err=None
#     return {
#         'statusCode': '400' if None else '200',
#         'body': None.message if None else json.dumps(response),
#         'headers': {
#             'Content-Type': 'application/json',
#             "Access-Control-Allow-Origin":"*",
#             "Access-Control-Allow-Credentials" : True,
#         },
#     }

