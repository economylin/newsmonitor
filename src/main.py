import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import configmanager.handlers
import webservice.handlers
import webservice.handlersapi

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/', MainPage),
('/configitem', configmanager.handlers.MainPage),
('/fetch', webservice.handlers.FetchPage),
('/parse', webservice.handlers.ParsePage),
('/api/fetch/request', webservice.handlersapi.FetchRequest),
('/api/fetch/response', webservice.handlersapi.FetchResponse),
],
                              debug=True)

