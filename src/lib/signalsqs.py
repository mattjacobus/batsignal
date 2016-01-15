import json
import boto3
import botocore
import logging

LOG = logging.getLogger(__name__)
sqs = boto3.resource('sqs', region_name='us-east-1')

# Returns list of urls pointing to signal in S3 or 
# None if cannot find queue for device
def receive_signal_info(device_id, key):
    try:
        queue = sqs.get_queue_by_name(QueueName=device_id)
    except botocore.exceptions.ClientError as e:
        return None
    signal_urls = []
    messages = queue.receive_messages(WaitTimeSeconds=5)
    for m in messages:
        try:
            signal = json.loads(m.body)
            signal_urls.append(signal[key])
        except ValueError:
            LOG.error('Could not parse json or find url: ' + m.body)
    return (signal_urls, messages)

