import logging
import requests
import os
from requests_aws4auth import AWS4Auth

LOG = logging.getLogger(__name__)

HOME = '/home/ec2-user/batsignal'
SIGNAL_DIR = HOME+'/signal'
DEVICE_FILE = HOME+'/config/device_id'
LOG_FILE = HOME+'/log/log'

AUTH = AWS4Auth('AKIAJ22GKBOOE27ZIL6A', 'nFF5lforu0rQZ8ipkVrVw0DiLxBqfdKTUCncI5uP', 'us-east-1', 's3')

logging.basicConfig(filename=LOG_FILE,level=logging.INFO)

def get_device_id():
    with open(DEVICE_FILE, 'r') as f:
        return f.readline().strip()
    LOG('Could not find device file: ' + DEVICE_PATH)
    return None

def get_last_seq():
    signals = os.listdir(SIGNAL_DIR)
    if not signals:
        return 0
    signals.sort()
    last = signals[-1]
    return int(last.split('_')[0])

def save_all_signals():
    device_id = get_device_id()
    for url in get_signal_urls(device_id):
        save_signal(url)

def get_signal_urls(device_id):
    seq = get_last_seq() + 1
    url = 'https://2n45zoglg7.execute-api.us-east-1.amazonaws.com/prod/signal/{}'.format(device_id)
    try:
        r = requests.get(url, params={'since_seq': seq})
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
    seq = os.path.basename(url)
    try:
        r = requests.get(url, auth=AUTH)
        if r.status_code == 200:
            try:
                d = r.json()
                date = d['received'].split('T')[0]
                fn = '{}_{}'.format(seq, date)
                path = os.path.join(SIGNAL_DIR, fn)
                with open(path, 'w') as f:
                    f.write(r.content)
            except:
                LOG.error('Signal not json or has no received datetime: {}'.format(url))
        else:
            LOG.error('Bad response when retrieving signal {}: {}'.\
                      format(url, r))
    except requests.exceptions.RequestException as e:
        LOG.exception('Could not retrieve signal from {}: {}'.format(url, e))
    
if __name__ == '__main__':
    save_all_signals()
