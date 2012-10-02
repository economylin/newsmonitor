import json
import logging
from md5 import md5
import urllib2

from google.appengine.api import taskqueue

import webapp2

from contentdetector import ContentFetcher, HtmlContentParser

def _calculateHash(items):
    lines = []
    for item in items:
        url = item.get('url')
        title = item.get('title')
        if url:
            lines.append(url)
        elif title:
            lines.append(title)
    return md5(''.join(lines)).hexdigest()

class FetchRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        # Use queue so we have a longer deadline.
        taskqueue.add(queue_name="fetch", payload=rawdata, url='/api/fetch/response')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')


class FetchResponse(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        fetchurl = data['fetchurl']
        fetcher = ContentFetcher(fetchurl)
        _, _, content = fetcher.fetch()
        items = []
        responseData = {}
        if content:
            parser = HtmlContentParser()
            items = parser.parse(fetchurl, content, data['selector'])
            if not items:
                logging.error('Failed to parse content form %s by %s.' % (data['fetchurl'], data['selector']))
        else:
            logging.error('Failed to fetch content form %s.' % (data['fetchurl'], ))
        if items:
            fetchhash = _calculateHash(items)
            if fetchhash != data['fetchhash']:
                responseData = {
                    'request': data,
                    'result': {
                        'items': items,
                        'fetchhash': fetchhash,
                    },
                }
        if responseData:            
            f = urllib2.urlopen(data['callback'], json.dumps(responseData))
            response = f.read()
            f.close()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Response is generated.')

