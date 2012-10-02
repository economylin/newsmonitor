import xml.sax.saxutils
import webapp2
import os
from google.appengine.ext.webapp import template
from contentdetector import ContentFetcher, HtmlContentParser

class FetchPage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
        }
        self._render(templateValues)

    def post(self):
        url = self.request.get('url')
        encoding = self.request.get('encoding')
        preventcache = not not self.request.get('preventcache')
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

class ParsePage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
        }
        self._render(templateValues)

    def post(self):
        url = self.request.get('url')
        content = xml.sax.saxutils.unescape(self.request.get('content'))
        css = self.request.get('css')
        if css:
            parser = HtmlContentParser()
            items = parser.parse(content, css)
        else:
            items = []
        templateValues = {
            'url': url,
            'content': content,
            'css': css,
            'items': items,
        }
        self._render(templateValues)

