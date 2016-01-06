from __future__ import print_function
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import \
    UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute

class SMS(Model):
    class Meta:
        table_name = 'sms'
    number = UnicodeAttribute(hash_key=True)
    group_id = UnicodeAttribute()

class Group(Model):
    class Meta:
        table_name = 'group'
    group_id = UnicodeAttribute(hash_key=True)
    dest = UnicodeAttribute(range_key=True)

class Device(Model):
    class Meta:
        table_name = 'device'
    device_id = UnicodeAttribute(hash_key=True)
    seq = NumberAttribute(default=0)

class DeviceSignal(Model):
    class Meta:
        table_name = 'device_signal'
    device_id = UnicodeAttribute(hash_key=True)
    seq = NumberAttribute(range_key=True)
    from_name = UnicodeAttribute(attr_name='from')
    to_name = UnicodeAttribute(attr_name='to')
    content_type = UnicodeAttribute(attr_name='type')
    text = UnicodeAttribute()
    received = UTCDateTimeAttribute()

def create_table(table):
    if not table.exists():
        table.create_table(read_capacity_units=1, 
                           write_capacity_units=1, wait=True)

def create_schema():
    for table in [SMS, Group, Device, DeviceSignal]:
        create_table(table)

def add_device(num, name):
    SMS(num, group_id=name).save()
    Group(name, 'device:'+name).save()
    Device(name).save()

if __name__ == '__main__':
    create_schema()
