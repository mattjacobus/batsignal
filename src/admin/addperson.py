from __future__ import print_function
from schema import SMSToPerson
import uuid
import sys

def add_person_sms(num, name):
    SMSToPerson(num, name=name).save()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python addperson.py [num] [name]')
        sys.exit(1)
    add_person_sms(sys.argv[1], sys.argv[2])

