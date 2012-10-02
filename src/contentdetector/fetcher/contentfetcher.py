# -*- coding: utf-8 -*-

from commonutil import dateutil
import base64
import logging
import urllib2
import chardet

_FETCH_TIMEOUT = 20

class ContentFetcher(object):
    def __init__(self, url, encoding=None, preventCache=False):
        self.url = url
        self.encoding = encoding
        self.preventCache = preventCache

    def authenticate(self, req):        
        pass

    def fetch(self):
        fetchUrl = None
        encodingUsed = None
        try:
            fetchUrl = self.url
            if self.preventCache:
                if fetchUrl.find('?') > 0:
                    fetchUrl += '&'
                else:
                    fetchUrl += '?'
                fetchUrl += '_preventCache=' + str(dateutil.getIntByMinitue())
            req = urllib2.Request(fetchUrl)
            self.authenticate(req)
            res = urllib2.urlopen(req, timeout=_FETCH_TIMEOUT)
            content = res.read()
            res.close()
            encodingUsed = self.encoding
            if not encodingUsed:
            	detectResult = chardet.detect(content)
                if detectResult:
                    encodingUsed = detectResult['encoding']
                else:
                    encodingUsed = 'utf-8'
                    logging.error('chardet failed to detect encoding from %s.' % (fetchUrl,))

            return fetchUrl, encodingUsed, unicode(content, encodingUsed,'ignore')
        except Exception, err:
            response = 'Error on fetching data from %s:%s.' % (self.url, err)
            logging.exception(response)
            return fetchUrl, encodingUsed, None

class BasicAuthContentFetcher(ContentFetcher):
    def __init__(self, url, username, password, encoding=None, preventCache=False):
        super(BasicAuthContentFetcher, self).__init__(url, encoding=encoding, preventCache=preventCache)
        self.username = username
        self.password = password

    def authenticate(self, req):        
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  'Basic %s' % base64string
        req.add_header('Authorization', authheader)

