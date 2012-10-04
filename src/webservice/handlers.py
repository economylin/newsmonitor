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
        }
        self._render(templateValues)

    def post(self):
        slug = self.request.get('slug')
        name = self.request.get('name')
        url = self.request.get('url')
        preventcache = not not self.request.get('preventcache')
        useragent = self.request.get('useragent')
        cookie = self.request.get('cookie')
        timeout = self.request.get('timeout')
        if timeout:
            timeout = int(timeout)
        encoding = self.request.get('encoding')
        fetchurl = self.request.get('fetchurl')
        parsedencoding = self.request.get('parsedencoding')

        content = self.request.get('content')
        selector = self.request.get('selector')
        items = []

        if not content and url:
            fetcher = ContentFetcher(url, preventcache=preventcache,
                           useragent=useragent, cookie=cookie,
                           timeout=timeout, encoding=encoding
                         )
            fetchurl, parsedencoding, content = fetcher.fetch()
        if content and selector:
            parser = HtmlContentParser()
            items = parser.parse(url, content, selector)
        newscenter = {
                    'slug': slug,
                    'name': name,
                    'fetchurl': url,
                    'selector': selector,
        }
        if preventcache:
            newscenter['preventcache'] = preventcache
        if useragent:
            newscenter['useragent'] = useragent
        if cookie:
            newscenter['cookie'] = cookie
        if timeout:
            newscenter['timeout'] = int(timeout)
        if encoding:
            newscenter['encoding'] = encoding
        templateValues = {
            'url': url,
            'preventcache': preventcache,
            'useragent': useragent,
            'cookie': cookie,
            'timeout': timeout,
            'encoding': encoding,
            'content': content,
            'fetchurl': fetchurl,
            'parsedencoding': parsedencoding,
            'content': content,
            'selector': selector,
            'items': items,
            'newscenter': json.dumps(newscenter),
        }
        self._render(templateValues)

