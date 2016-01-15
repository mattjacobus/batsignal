import boto3
import json
from signals3 import BUCKET, get_key, get_signal_url
from signaljson import SignalEncoder

s3 = boto3.resource('s3')
sqs = boto3.resource('sqs', region_name='us-east-1')

def post(device_id, signal_id, signal_notif, signal):
    # put signal in s3
    signal_json = json.dumps(signal, indent=4, cls=SignalEncoder)
    s3.Object(BUCKET, get_key(device_id, signal_id)).put(Body=signal_json)

    # post a notification on sqs
    queue = sqs.get_queue_by_name(QueueName=device_id)
    signal_notif['url'] = get_signal_url(device_id, signal_id)
    notif_json = json.dumps(signal_notif, indent=4, cls=SignalEncoder)
    response = queue.send_message(MessageBody=notif_json)

