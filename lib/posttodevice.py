import boto3
import json
import decimal
import datetime

BUCKET = 'batsignl'
SEQ_FORMAT = '{:06}'
s3 = boto3.resource('s3')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super(DecimalEncoder, self).default(o)

def format_seq(seq):
    return SEQ_FORMAT.format(seq)

def get_key(device_id, seq):
    return 'signal/{}/{}'.format(device_id, format_seq(seq))    

def post(device_id, seq, signal):
    mj = json.dumps(signal, indent=4, cls=DecimalEncoder)
    s3.Object(BUCKET, get_key(device_id, seq)).put(Body=mj)

def get_signal_url(device_id, seq):
    return 'https://{}.s3.amazonaws.com/{}'.\
        format(BUCKET, get_key(device_id, seq))
