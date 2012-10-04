# -*- coding: utf-8 -*-
import base64
import logging
import urllib2

import chardet

from commonutil import dateutil
import globalconfig

class ContentFetcher(object):
    def __init__(self, url, preventcache=False, useragent=None, cookie=None, timeout=None, encoding=None):
        self.url = url
        self.preventcache = preventcache
        self.useragent = globalconfig.getUserAgent(useragent)
        self.cookie = cookie

        if timeout:
            self.timeout = timeout
        else:
            self.timeout = globalconfig.getFetchTimeout()
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
            if self.cookie:
                req.add_header('Cookie', self.cookie)
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

