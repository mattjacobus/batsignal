from __future__ import print_function
from schema import SMS, Group, Dest
import uuid
import sys

def add_device(num, name):
    id = str(uuid.uuid4())
    SMS(num, group_id=id).save()
    Group(id, name=name).save()
    Dest(id, 'device:'+id).save()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python adddevice.py [num] [name]')
        sys.exit(1)
    add_device(sys.argv[1], sys.argv[2])

