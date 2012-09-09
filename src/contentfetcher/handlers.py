import cgi
import webapp2
import os
from google.appengine.ext.webapp import template
from contentfetcher import ContentFetcher

class FetcherPage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
            'encoding': 'UTF-8',
        }
        self._render(templateValues)

    def post(self):
        url = cgi.escape(self.request.get('url'))
        encoding = cgi.escape(self.request.get('encoding'))
        preventcache = not not cgi.escape(self.request.get('preventcache'))
        content = None
        fetchUrl = None
        if url and encoding:
            fetcher = ContentFetcher(url, encoding, preventcache)
            fetchUrl, content = fetcher.fetch()
        templateValues = {
            'url': url,
            'encoding': encoding,
            'preventcache': preventcache,
            'content': content,
            'fetchurl': fetchUrl,
        }
        self._render(templateValues)

