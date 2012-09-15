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
        }
        self._render(templateValues)

    def post(self):
        url = cgi.escape(self.request.get('url'))
        encoding = cgi.escape(self.request.get('encoding'))
        preventcache = not not cgi.escape(self.request.get('preventcache'))
        content = None
        fetchUrl = None
        encodingUsed = None
        if url:
            fetcher = ContentFetcher(url, encoding, preventcache)
            fetchUrl, encodingUsed, content = fetcher.fetch()
        templateValues = {
            'url': url,
            'encoding': encoding,
            'preventcache': preventcache,
            'content': content,
            'fetchurl': fetchUrl,
            'encodingused': encodingUsed,
        }
        self._render(templateValues)

