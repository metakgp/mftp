import update
import os
from concurrent.futures import ThreadPoolExecutor
import tornado.web
import tornado.ioloop
from tornado import gen
import requests
import settings

requests.packages.urllib3.disable_warnings()

ioloop = tornado.ioloop.IOLoop.current()
executor = ThreadPoolExecutor(max_workers=2)


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
        except Exception as e:
            print "There was an error!"
            print e
    yield executor.submit(func)
    print 'run_updates done'


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        return

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', PingHandler)
    ])
    app.listen(os.environ['PORT'])
    run_updates()
    tornado.ioloop.PeriodicCallback(run_updates,
                                    6 * 1000).start()
    ioloop.start()
