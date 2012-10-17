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
        if action == 'JSON':
            jsonstr = self.request.get('jsonstr')
            newssource = json.loads(jsonstr)
            parsedencoding = ''
            parsedurl = ''
            content = ''
        else:
            newssource = {}
            newssource['active'] = bool(self.request.get('active'))
            newssource['slug'] = self.request.get('slug')
            newssource['name'] = self.request.get('name')
            newssource['fetchurl'] = self.request.get('fetchurl')
            newssource['preventcache'] = bool(self.request.get('preventcache'))
            newssource['useragent'] = self.request.get('useragent')
            newssource['proxy'] = self.request.get('proxy')
            newssource['cookie'] = self.request.get('cookie')
            timeout = self.request.get('timeout')
            if timeout:
                newssource['timeout'] = int(timeout)
            newssource['encoding'] = self.request.get('encoding')
            jsonstr = json.dumps(newssource)
            parsedencoding = self.request.get('parsedencoding')
            parsedurl = self.request.get('parsedurl')
            if parsedurl and not parsedurl.startswith(newssource.get('fetchurl')):
                newssource['selector'] = ''
                content = ''
            else:
                newssource['selector'] = self.request.get('selector')
                content = self.request.get('content')

        if 'active' not in newssource:
            newssource['active'] = True

        items = []
        selector = newssource.get('selector')
        fetchurl = newssource.get('fetchurl')

        if (not content or not selector) and fetchurl:
            fetcher = ContentFetcher(fetchurl, preventcache=newssource.get('preventcache'),
                           useragent=newssource.get('useragent'), proxy=newssource.get('proxy'),
                           cookie=newssource.get('cookie'),
                           timeout=newssource.get('timeout'), encoding=newssource.get('encoding')
                         )
            parsedurl, parsedencoding, content = fetcher.fetch()
        if content and selector:
            parser = HtmlContentParser()
            items = parser.parse(fetchurl, selector + '@', content)
        templateValues = {
            'newssource': newssource,
            'content': content,
            'parsedencoding': parsedencoding,
            'parsedurl': parsedurl,
            'items': items,
            'jsonstr': jsonstr,
        }
        self._render(templateValues)

