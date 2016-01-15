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
    name = UnicodeAttribute()

class Dest(Model):
    class Meta:
        table_name = 'dest'
    group_id = UnicodeAttribute(hash_key=True)
    dest = UnicodeAttribute(range_key=True)

class SMSToPerson(Model):
    class Meta:
        table_name = 'sms_to_person'
    number = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()

def create_table(table):
    if not table.exists():
        table.create_table(read_capacity_units=1, 
                           write_capacity_units=1, wait=True)

def create_schema():
    for table in [SMS, Group, Dest, SMSToPerson]:
        create_table(table)

if __name__ == '__main__':
    create_schema()
