import json
import logging
import time
import urllib2

from google.appengine.api import taskqueue

import webapp2

from commonutil import stringutil
from contentfetcher import ContentFetcher
from contentdetector import HtmlContentParser

_URL_TIMEOUT = 30
_FETCH_TRYCOUNT = 3
_CALLBACK_TRYCOUNT = 3

def _calculateHash(items):
    lines = []
    for item in items:
        url = item.get('url')
        if url:
            lines.append(url)
        else:
            title = item.get('title')
            if title:
                lines.append(title)
    return stringutil.calculateHash(lines)

def _fetchContent(data, triedcount):
    fetchurl = data['fetchurl']
    header = data.get('header')
    encoding = data.get('encoding')
    fetcher = ContentFetcher(fetchurl, header=header,
                                encoding=encoding, tried=triedcount)
    _, _, content = fetcher.fetch()
    return content

def _parseItems(fetchurl, selector, content):
    parser = HtmlContentParser()
    items = parser.parse(fetchurl, selector, content)
    return items

def _pushItemsBack(callbackurl, responseData):
    try:
        f = urllib2.urlopen(callbackurl, json.dumps(responseData),
                            timeout=_URL_TIMEOUT)
        f.read()
        f.close()
        return True
    except Exception:
        logging.exception('Failed to post data to "%s".' % (callbackurl, ))
    return False

class FetchRequest(webapp2.RequestHandler):
    def post(self):
        rawdata = self.request.body
        taskqueue.add(queue_name="default", payload=rawdata, url='/fetch/batch/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')


class BatchFetchRequest(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        callbackurl = data['callbackurl']
        items = data['items']
        for item in items:
            item['callbackurl'] = callbackurl
            rawdata = json.dumps(item)
            taskqueue.add(queue_name="default", payload=rawdata, url='/fetch/single/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Put fetch task into queue.')


class SingleFetchResponse(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        data = json.loads(self.request.body)
        triedcount = data.get('triedcount', 0)
        monitorRequest = data['request']
        content = _fetchContent(monitorRequest, triedcount)
        slug = monitorRequest['slug']
        fetchurl = monitorRequest['fetchurl']
        if not content:
            triedcount += 1
            leftcount = _FETCH_TRYCOUNT - triedcount
            message = 'Failed to fetch content form %s for %s, lefted: %s.' % (
                        fetchurl, slug, leftcount, )
            logging.error(message)
            self.response.out.write(message)
            if leftcount > 0:
                data['triedcount'] = triedcount
                taskqueue.add(queue_name="default", payload=json.dumps(data),
                            url='/fetch/single/')
            return

        selector = monitorRequest['selector']
        items = _parseItems(fetchurl, selector, content)
        if not items:
            message = 'Failed to parse items from %s for %s by %s.' % (
                                  fetchurl, slug, selector)
            logging.error(message)
            self.response.out.write(message)
            return
        message = 'Items got for %s.' % (slug, )
        logging.info(message)
        self.response.out.write(message)

        oldhash = monitorRequest['fetchhash']
        fetchhash = _calculateHash(items)
        if oldhash == fetchhash:
            return

        callbackurl = data['callbackurl']
        responseData = {
                'origin': data['origin'],
                'result': {
                    'items': items,
                    'fetchhash': fetchhash,
                },
        }
        doCallback = False
        for i in range(_CALLBACK_TRYCOUNT):
            if _pushItemsBack(callbackurl, responseData):
                doCallback = True
                break
            leftcount = _CALLBACK_TRYCOUNT - 1 - i
            message = 'Failed to push items back for %s to %s, try count left: %s.' % (
                              slug, callbackurl, leftcount)
            logging.info(message)
            self.response.out.write(message)
            if leftcount > 0:
                time.sleep(2)
        if not doCallback:
            return

        message = 'Push items back for %s to %s.' % (slug, callbackurl)
        logging.info(message)
        self.response.out.write(message)

