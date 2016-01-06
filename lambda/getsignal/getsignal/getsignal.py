from __future__ import print_function
from schema import DeviceSignal
from posttodevice import get_signal_url
from datetime import datetime
import json

from datetime import datetime, timedelta

def get_signals_since(device_id, seq):
    yest = datetime.now()+timedelta(days=-1)
    signals = DeviceSignal.query(device_id, seq__ge=seq, 
                                 received__ge=yest, limit=10)
    return [get_signal_url(device_id, s.seq) for s in signals]

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + str(context))

    return {'signals': 
            get_signals_since(event['device_id'], int(event['since_seq']))}
