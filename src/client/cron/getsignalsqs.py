#!/usr/bin/python
import logging
import logging.handlers
import os
import sys
import argparse
import boto3
from signalsqs import receive_signal_info
from signals3 import BUCKET, get_key

DEBUG = False
HOME = '/home/ec2-user/batsignal'
SIGNAL_DIR = HOME+'/signal'
DEVICE_FILE = HOME+'/config/device_id'
LOG_FILE = HOME+'/log/getsignal.log'

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
              LOG_FILE, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)

s3_client = boto3.client('s3')

def get_device_id():
    with open(DEVICE_FILE, 'r') as f:
        return f.readline().strip()
    LOG.error('Could not find device file: ' + DEVICE_PATH)
    return None

def save_all_signals():
    device_id = get_device_id()
    signal_ids, messages = receive_signal_info(device_id, 'signal-id')
    for signal_id, message in zip(signal_ids, messages):
        if save_signal(device_id, signal_id):
            message.delete()

# Returns True if done with message forever
# Returns False when we want to get the message again in the future
def save_signal(device_id, signal_id):
    key = get_key(device_id, signal_id)
    path = os.path.join(SIGNAL_DIR, signal_id)
    try:
        s3_client.download_file(BUCKET, key, path)
    except Exception as e:
        LOG.error('Cannot download signal {} to {}: {}'.format(key, path, e))
        return False
    if DEBUG:
        debug(key, path)
    return True

def debug(key, path):
    print('downloaded ' + key)
    with open(path, 'r') as f:
        print(f.read())

def repeat():
    while True:
        save_all_signals()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--once', help='get signals once',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='print signal when get it',
                        action='store_true')
    args = parser.parse_args()
    if args.debug:
        DEBUG = True
    if args.once:
        save_all_signals()
    else:
        repeat()
