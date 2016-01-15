#!/usr/bin/python
import logging
import logging.handlers
import requests
import os
from requests_aws4auth import AWS4Auth

HOME = '/home/ec2-user/batsignal'
SIGNAL_DIR = HOME+'/signal'
DEVICE_FILE = HOME+'/config/device_id'
LOG_FILE = HOME+'/log/getsignal.log'

AUTH = AWS4Auth('AKIAJ22GKBOOE27ZIL6A', 'nFF5lforu0rQZ8ipkVrVw0DiLxBqfdKTUCncI5uP', 'us-east-1', 's3')

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
    for url in get_signal_urls(device_id):
        save_signal(url)

def get_signal_urls(device_id):
    url = 'https://2n45zoglg7.execute-api.us-east-1.amazonaws.com/prod/signal/{}'.format(device_id)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            signals = r.json()['signals']
            return signals
        else:
            LOG.error('Bad response when retrieving index: {}'.format(r))
    except requests.exceptions.RequestException as e:
        LOG.exception('Could not retrieve signal index from url {}: {}'.\
                      format(url, e))
    return []

def save_signal(url):
    id = os.path.basename(url)
    try:
        r = requests.get(url, auth=AUTH)
        if r.status_code == 200:
            try:
                d = r.json()
                path = os.path.join(SIGNAL_DIR, id)
                with open(path, 'w') as f:
                    f.write(r.content)
                LOG.info('Wrote signal %s' % id)
            except:
                LOG.error('Signal not json or has no received datetime: {}'.format(url))
        else:
            LOG.error('Bad response when retrieving signal {}: {}'.\
                      format(url, r))
    except requests.exceptions.RequestException as e:
        LOG.exception('Could not retrieve signal from {}: {}'.format(url, e))

def repeat():
    while True:
        save_all_signals()
    
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        repeat()
    else:
        save_all_signals()
