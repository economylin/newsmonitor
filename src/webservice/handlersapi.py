import json
import logging
from md5 import md5
import urllib2

from google.appengine.api import taskqueue

import webapp2

from contentdetector import ContentFetcher, HtmlContentParser

def _calculateHash(newscenterSlug, items):
    lines = []
    for item in items:
        url = item.get('url')
        title = item.get('title')
        if url:
            if type(url) == unicode:
                lines.append(url.encode('utf-8','ignore'))
            else:
                lines.append(url)
        elif title:
            if type(title) == unicode:
                lines.append(title.encode('utf-8','ignore'))
            else:
                lines.append(title)
    value = ''
    try:
        value = md5(''.join(lines)).hexdigest()
    except:
        logging.exception('%s: %s.' % (newscenterSlug, items, ))
    return value

class FetchRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/fetch/batch')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

class BatchFetchRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        items = data.get['items']
        for item in items:
            rawdata = json.dumps(item)
            taskqueue.add(queue_name="default", payload=rawdata, url='/fetch/single')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Put fetch task into queue.')


class SingleFetchResponse(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        newscenterSlug = data['slug']
        fetchurl = data['fetchurl']
        preventcache = data.get('preventcache')
        useragent = data.get('useragent')
        cookie = data.get('cookie')
        timeout = data.get('timeout')
        encoding = data.get('encoding')
        fetcher = ContentFetcher(fetchurl, preventcache=preventcache,
                         useragent=useragent, cookie=cookie,
                         timeout=timeout, encoding=encoding)
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
            fetchhash = _calculateHash(newscenterSlug, items)
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

