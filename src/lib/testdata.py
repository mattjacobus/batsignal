from __future__ import print_function
from schema import add_single_device, queue_sms

def main():
    #add_single_device('+3473452234', 'Jacobus')
    queue_sms('+3473452234', '+9176478688', 'text', 'Hello world!')

if __name__ == '__main__':
    main()



