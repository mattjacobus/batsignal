from __future__ import print_function

import json
import decimal
import datetime
import sys

sys.path.insert(0, '/home/ec2-user/src/boto3')
import boto3

client = boto3.client('apigateway', endpoint_url='https://apigateway.us-east-1.amazonaws.com')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super(DecimalEncoder, self).default(o)

def create_api(name):
    response = client.create_rest_api(name='sms')
    print("apigateway.create_rest_api:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))
    return response['id']

def get_first_resource(api_id):
    response = client.get_resources(restApiId=api_id)
    print("apigateway.get_resources:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))
    return response['items'][0]['id']

def create_resource(api_id, name):
    root_resource_id = get_first_resource(api_id)
    response = client.create_resource(restApiId=api_id,
                                      parentId=root_resource_id, 
                                      pathPart='sms')
    print("apigateway.create_resource:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))
    return response['id']

def create_method(api_id, resource_id, http_method):
    response = client.put_method(restApiId=api_id, 
                                 resourceId=resource_id,
                                 httpMethod=http_method, 
                                 authorizationType='NONE')
    print("put_method:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

def create_integration_request(api_id, resource_id, http_method, template):
    response = client.put_integration(restApiId=api_id, 
                                      resourceId=resource_id, 
                                      httpMethod=http_method,
                                      type='AWS',
                                      uri='arn:aws:lambda:us-east-1:736483223819:function:SMS',
                                      requestTemplates={
                                          'application/json':request_template
                                      }
    )
    print("put_integration:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

def create_integration_response(api_id, resource_id, http_method, template):
    response = client.put_integration_response(restApiId=api_id,
                                               resourceId=resource_id,
                                               httpMethod='GET', 
                                               type='AWS',
                                               responseTemplates={
                                                   'application/json':response_template
                                               }
    )
    print("put_integration_response:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

def create_api_resource_and_method(api_name, resource_name, method, 
                                   request_template=None, 
                                   response_template=None):
    api_id = create_api(api_name)
    resource_id = create_resource(api_id, resource_name)
    create_method(api_id, resource_id, method)
    if request_template:
        create_integration_request(api_id, resource_id, method, 
                                   request_template)
    if response_template:
        create_integration_response(api_id, resource_id, method,
                                    response_template)

request_template = '''{
    "message": "$input.params('Body')",
    "from": "$input.params('From')",
    "to": "$input.params('To')"
}
'''

response_template = '''<?xml version="1.0" encoding="UTF-8"?>
#set($inputRoot = $input.path('$'))
<Response>
    <Message>$inputRoot.reply</Message>
</Response>
'''

create_api_resource_and_method('sms3', 'smsp3', 'GET',
                               request_template=request_template, 
                               response_template=response_template)
