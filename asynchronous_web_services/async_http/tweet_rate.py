import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

import urllib
import json
import datetime
import time
import oauth2 as oauth

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

consumer_key = "bZzeXGYz1KpJFtDOhL6iA"
consumer_secret = "lXtNjEYvFFy0p0rAZ39g5qRzXAVzmHHu6DXi6jxCM8"
access_token = "43530233-AMI6KwoJxrjhpjYhzGSeBGTDNDL31glyS7lKYKK5h"
access_secret = "an3tGgmAlM3J3X7vz3YdFYu87cKwHtTfUKTqqIoY5A"


def request_twitter(url, key, secret, http_method = 'GET', post_body = '', http_headers = ''):
    consumer = oauth.Consumer(key = consumer_key, secret = consumer_secret)
    token = oauth.Token(key = key, secret = secret)
    client = oauth.Client(consumer, token)

    request = client.request(
        url,
        method = http_method,
        body = post_body,
        headers = http_headers)

    return request

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument('q')
        request, response = request_twitter('https://api.twitter.com/1.1/search/tweets.json?' + \
                                            urllib.urlencode({'q': query, "result_type": "recent", "count": 100 }),
                                            access_token,
                                            access_secret)
        body = json.loads(response)
        result_count = len(body['statuses'])
        now = datetime.datetime.utcnow()
        raw_oldest_tweet_at = body['statuses'][-1]['created_at']
        oldest_tweet_at = datetime.datetime.strptime(raw_oldest_tweet_at,
                "%a %b %d %H:%M:%S +0000 %Y")
        seconds_diff = time.mktime(now.timetuple()) - \
                time.mktime(oldest_tweet_at.timetuple())
        tweets_per_second = float(result_count) / seconds_diff
        self.write("""
<div style="text-align: center">
	<div style="font-size: 72px">%s</div>
	<div style="font-size: 144px">%.02f</div>
	<div style="font-size: 24px">tweets per second</div>
</div>""" % (query, tweets_per_second))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
