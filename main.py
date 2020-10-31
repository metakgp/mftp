import update
import os
from concurrent.futures import ThreadPoolExecutor
import tornado.web
import tornado.ioloop
from tornado import gen
import requests
import datetime
import traceback
import sys
import export_database

requests.packages.urllib3.disable_warnings()

ioloop = tornado.ioloop.IOLoop.current()
UPDATE_PERIOD = 2 * 60 * 1000


@gen.coroutine
def run_updates():
    def func():
        # try:
        #     print 'Checking companies...'
        #     update.check_companies()
        # except Exception as e:
        #     print e
        try:
            print 'Checking notices...'
            update.check_notices()
        except:
            print "Unhandled error occured :\n{}".format(traceback.format_exc())

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            yield gen.with_timeout(datetime.timedelta(UPDATE_PERIOD/1000.0),
                                   executor.submit(func))
        print 'run_updates done'
    except gen.TimeoutError:
        print 'run_updates timed out'


class PingHandler(tornado.web.RequestHandler):
    def head(self):
        return

    def get(self):
        return

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', PingHandler)
    ])
    app.listen(os.environ['PORT'])
    run_updates()
    tornado.ioloop.PeriodicCallback(run_updates,
                                    UPDATE_PERIOD).start()
    ioloop.start()
