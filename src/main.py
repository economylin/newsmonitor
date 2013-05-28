import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import monitor.handlers
import monitor.handlersapi

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/', MainPage),
('/fetch/', monitor.handlers.FetchPage),
('/api/fetch/', monitor.handlersapi.FetchRequest),
('/fetch/batch/', monitor.handlersapi.BatchFetchRequest),
('/fetch/single/', monitor.handlersapi.SingleFetchResponse),
],
debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'))

