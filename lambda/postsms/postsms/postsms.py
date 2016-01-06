from __future__ import print_function
from schema import SMS, Group, Device, DeviceSignal
import rendertext
from getimage import get_image
import posttodevice
import json

from datetime import datetime

def post_sms(to_num, from_num, content_type, text, images):
    sms = SMS.get(to_num)
    for group in Group.query(sms.group_id):
        type, device_id = group.dest.split(':')
        if type == 'device':
            post_sms_to_device(device_id, to_num, from_num,
                                content_type, text, images)

def post_sms_to_device(device_id, to_num, from_num, content_type, text, images):
    # increment seq in device table
    device = Device.get(device_id)
    device.update_item('seq', 1, action='add')

    # create a new signal in DeviceSignal table
    signal = DeviceSignal(device_id, device.seq, to_name=to_num, 
                          from_name=from_num, content_type=content_type,
                          text=text, received=datetime.now())
    signal.save()

    # render and post json to device
    to_name = to_num
    from_name = from_num
    signal = {'from':from_num, 'to':to_num, 'content-type': 'ppm',
              'received':datetime.now()}
    if text:
        signal['ppm'] = rendertext.render_to_image(text, 
                                                   from_name=from_name, 
                                                   to_name=to_name)
    if images:
        signal['images'] = images
    posttodevice.post(device_id, device.seq, signal)

def get_images(event):
    num_media = int(event['NumMedia'])
    return [get_image(event['MediaUrl%d'%i], event['MediaContentType%d'%i])
              for i in range(0, num_media)]

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))

    seq = post_sms(event['to'], event['from'], 'text', event['message'],
                   get_images(event))
    return {'reply': 'sent message: ' + event['message']}
