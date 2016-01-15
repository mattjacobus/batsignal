from __future__ import print_function
from schema import SMS, Group, Dest, SMSToPerson
from rendersms import render_sms, render_images
import posttodevice
import json
import copy
import uuid

from datetime import datetime

def post_sms(to_num, from_num, content_type, text, images):
    to_names = []
    sms = SMS.get(to_num)
    group = Group.get(sms.group_id)
    person = SMSToPerson.get(from_num)
    
    for dest in Dest.query(sms.group_id):
        type, device_id = dest.dest.split(':')
        if type == 'device':
            to_name = post_sms_to_device(device_id, group.name, person.name,
                                         content_type, text, images)
            to_names.append(to_name)
    if len(to_names) > 10:
        return 'Sent to %d people' % len(to_names)
    return  'Sent to %s.' % ' '.join(to_names)
            
def post_sms_to_device(device_id, to_name, from_name, content_type, text, images):
    signal_id = str(uuid.uuid4())
    
    # create signal and signal_notif dict (former doesn't have images)
    signal_notif = {'from':from_name, 'to':to_name, 'content-type': 'ppm',
                    'received':datetime.now(), 'signal-id': signal_id,
                    'message': text}
    signal = copy.deepcopy(signal_notif)
    signal['images'] = render_sms(to_name, from_name, text, images)

    posttodevice.post(device_id, signal_id, signal_notif, signal)
    return to_name

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))

    to_num = event['to']
    from_num = event['from']
    message = event.get('message', None)
    images = render_images(event)
    
    reply = post_sms(to_num, from_num, 'text', message, images)
    return {'reply': reply}
