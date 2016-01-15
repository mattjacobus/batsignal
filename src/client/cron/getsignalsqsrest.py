#!/usr/bin/python
import logging
import logging.handlers
import requests
import os
import sys
import json
from StringIO import StringIO
from requests_aws4auth import AWS4Auth
import xml.etree.ElementTree as ET
import urllib2

HOME = '/home/ec2-user/batsignal'
SIGNAL_DIR = HOME+'/signal'
DEVICE_FILE = HOME+'/config/device_id'
LOG_FILE = HOME+'/log/getsignal.log'

LOG = logging.getLogger('getsignal')
LOG.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
              LOG_FILE, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)

def get_device_id():
    with open(DEVICE_FILE, 'r') as f:
        return f.readline().strip()
    LOG('Could not find device file: ' + DEVICE_PATH)
    return None

def save_all_signals():
    device_id = get_device_id()
    urls, handles = get_signal_urls(device_id):
    for url, handle in zip(urls, handles):
        if save_signal(url):
            delete_message(handle)

def get_queue_url(device_id):
    return 'https://sqs.us-east-1.amazonaws.com/736483223819/'+device_id

def delete_message(device_id, handle):
    url = get_queue_url(device_id)

def get_urls_from_xml(content):
    ns = {'ns': 'http://queue.amazonaws.com/doc/2012-11-05/'}
    print 'content', content

    # Strip all namespace tags as per https://bugs.python.org/msg216774
    cf = StringIO(content)
    it = ET.iterparse(cf)
    for _, el in it:
        el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    root = it.root

    # Pull out url and handle (for deletion)
    urls = []
    handles = []
    for message in root.iter('Message'):
        for body in message.iter('Body'):
            bj = json.loads(urllib2.unquote(body.text))
            if not bj.has_key('url'):
                LOG.error('URL not found in message ' + bj)
            url = bj['url']
            urls.append(url)
        for receipt_handle in message.iter('ReceiptHandle'):
            handles.append(receipt_handle.text)
    return (urls, handles)

def get_signal_urls(device_id):
    url = get_queue(device_id)
    try:
        params = {
            'Action': 'ReceiveMessage',
            'WaitTimeSeconds': '20',
        }
        r = requests.get(url, params=params, auth=AUTH)
        if r.status_code == 200:
            print r.content
            urls, handles = get_urls_from_xml(r.content)
            print urls
            return urls, handles
        else:
            LOG.error('Bad response when retrieving index: {}'.format(r))
    except requests.exceptions.RequestException as e:
        LOG.exception('Could not retrieve signal index from url {}: {}'.\
                      format(url, e))
    return ([], [])

# Returns True if done with message forever
# Returns False when we want to get the message again in the future
def save_signal(url):
    id = os.path.basename(url)
    try:
        r = requests.get(url, auth=AUTH)
        if r.status_code == 200:
            try:
                path = os.path.join(SIGNAL_DIR, id)
                with open(path, 'w') as f:
                    f.write(r.content)
                LOG.info('Wrote signal %s' % id)
            except Exception as e:
                LOG.error('Cannot write signal {}: {}'.format(url, e))
                # cannot write, retry in future
                return False
        else:
            LOG.error('Bad response when retrieving signal {}: {}'.\
                      format(url, r))
            # s3 problem, retry in future
            return False
    except requests.exceptions.RequestException as e:
        LOG.exception('Could not retrieve signal from {}: {}'.format(url, e))
        # network problem, retry in future
        return False
    return True

def repeat():
    while True:
        save_all_signals()
    
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        repeat()
    else:
        save_all_signals()
