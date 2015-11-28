import erp
import time
import socket
import os

# bind to web port to keep Heroku from killing the process
s = socket.socket(socket.AF_INET)
try:
    s.bind((socket.gethostname(), int(os.environ['PORT'])))
    s.listen(10)
except KeyError:
    pass

while True:
    print 'Checking companies...'
    try:
        erp.check_companies()
    except Exception as e:
        print e
        time.sleep(30)
        continue
    print 'Sleeping for 2 minutes...'
    time.sleep(2 * 60)
