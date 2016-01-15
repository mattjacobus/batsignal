BUCKET = 'batsignl'

def get_key(device_id, signal_id):
    return 'signal/{}/{}'.format(device_id, signal_id)

def get_signal_url(device_id, signal_id):
    return 'https://{}.s3.amazonaws.com/{}'.\
        format(BUCKET, get_key(device_id, signal_id))

