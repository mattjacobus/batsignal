from __future__ import print_function
from signalsqs import receive_signal_info
import json

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))

    if not event.has_key('device_id'):
        return {'error': 'Must supply device id'}
    device_id = event['device_id']

    urls, messages = receive_signal_info(device_id, 'url')

    # TODO: should delete messages only after we've retrieved the signal
    # from S3 or we may lose them
    for m in messages:
        m.delete()

    if urls == None:
        return {'error': 'Unknown device id, ' + device_id}
    return {'signals': urls}
