import json
import os

from google.appengine.ext.webapp import template
import webapp2

from contentdetector import ContentFetcher, HtmlContentParser

class FetchPage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
            'newssource': {'active': True},
        }
        self._render(templateValues)

    def post(self):
        action = self.request.get('action')
        fetchurl = self.request.get('fetchurl')
        selector = self.request.get('selector')
        if action == 'JSON':
            jsonstr = self.request.get('jsonstr')
            newssource = json.loads(jsonstr)
        else:
            newssource = {}
            newssource['active'] = bool(self.request.get('active'))
            newssource['slug'] = self.request.get('slug')
            newssource['name'] = self.request.get('name')
            newssource['fetchurl'] = fetchurl
            newssource['preventcache'] = bool(self.request.get('preventcache'))
            newssource['useragent'] = self.request.get('useragent')
            newssource['proxy'] = self.request.get('proxy')
            newssource['cookie'] = self.request.get('cookie')
            timeout = self.request.get('timeout')
            if timeout:
                newssource['timeout'] = int(timeout)
            newssource['encoding'] = self.request.get('encoding')
            newssource['selector'] = selector
            jsonstr = json.dumps(newssource)

        if 'active' not in newssource:
            newssource['active'] = True

        parsedencoding = self.request.get('parsedencoding')
        parsedurl = self.request.get('parsedurl')
        content = self.request.get('content')
        items = []
        if (not content or not selector) and fetchurl:
            fetcher = ContentFetcher(fetchurl, preventcache=newssource['preventcache'],
                           useragent=newssource['useragent'], proxy=newssource['proxy'],
                           cookie=newssource['cookie'],
                           timeout=newssource.get('timeout'), encoding=newssource['encoding']
                         )
            parsedurl, parsedencoding, content = fetcher.fetch()
        if content and selector:
            parser = HtmlContentParser()
            items = parser.parse(selector, selector, content)
        templateValues = {
            'newssource': newssource,
            'content': content,
            'parsedencoding': parsedencoding,
            'parsedurl': parsedurl,
            'items': items,
            'jsonstr': jsonstr,
        }
        self._render(templateValues)

