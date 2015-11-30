import update
import os
import tornado.web
import tornado.ioloop

ioloop = tornado.ioloop.IOLoop.current()


def run_updates():
    try:
        print 'Checking companies...'
        update.check_companies()
    except Exception as e:
        print e
    try:
        print 'Checking notices...'
        update.check_notices()
    except Exception as e:
        print e


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
                                    120 * 1000).start()
    ioloop.start()
