# -*- coding: utf-8 -*-

from commonutil import dateutil
import base64
import logging
import urllib2
import chardet

_FETCH_TIMEOUT = 20
_USER_AGENT = {
    'ie': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'firefox': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
}

class ContentFetcher(object):
    def __init__(self, url, preventcache=False, useragent=None, timeout=None, encoding=None):
        self.url = url
        self.preventcache = preventcache
        self.useragent = _USER_AGENT.get(useragent, useragent) if useragent else None

        if timeout:
            self.timeout = timeout
        else:
            self.timeout = _FETCH_TIMEOUT
        self.encoding = encoding

    def authenticate(self, req):        
        pass

    def fetch(self):
        fetchUrl = None
        encodingUsed = None
        try:
            fetchUrl = self.url
            if self.preventcache:
                if fetchUrl.find('?') > 0:
                    fetchUrl += '&'
                else:
                    fetchUrl += '?'
                fetchUrl += '_preventCache=' + str(dateutil.getIntByMinitue())
            req = urllib2.Request(fetchUrl)
            self.authenticate(req)
            if self.useragent:
                req.add_header('User-agent', self.useragent)
            res = urllib2.urlopen(req, timeout=self.timeout)
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

