import erp
import time

while True:
    print 'Checking companies...'
    erp.check_companies()
    time.sleep(2 * 60)
