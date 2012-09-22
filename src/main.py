import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))


import webservice.handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


app = webapp2.WSGIApplication([
('/', MainPage),
('/fetch', webservice.handlers.FetchPage),
('/parse', webservice.handlers.ParsePage),
],
                              debug=True)

