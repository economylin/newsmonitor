# -*- coding: utf-8 -*-
import base64
import logging
import urllib2

import chardet

import globalconfig

class ContentFetcher(object):
    def __init__(self, url, header=None, encoding=None, tried=0):
        self.url = url
        self.header = header if header else {}
        self.encoding = encoding

        self.useragent = globalconfig.getUserAgent()
        defaultTimeout = globalconfig.getFetchTimeout()
        self.timeout = defaultTimeout * (tried + 1)

    def authenticate(self, req):        
        pass

    def fetch(self):
        fetchUrl = None
        encodingUsed = None
        try:
            fetchUrl = self.url
            req = urllib2.Request(fetchUrl)
            self.authenticate(req)
            if self.useragent:
                req.add_header('User-agent', self.useragent)
            for key, value in self.header.iteritems():
                req.add_header(key, value)
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            res = opener.open(req, timeout=self.timeout)
            content = res.read()
            res.close()
            encodingUsed = self.encoding
            if not encodingUsed:
            	detectResult = chardet.detect(content)
                if detectResult:
                    encodingUsed = detectResult['encoding']
                if not encodingUsed:
                    encodingUsed = 'utf-8'
                    logging.error('chardet failed to detect encoding from %s.' % (fetchUrl,))
            return fetchUrl, encodingUsed, unicode(content, encodingUsed,'ignore')
        except Exception, err:
            response = 'Error on fetching data from %s:%s.' % (self.url, err)
            logging.exception(response)
            return fetchUrl, encodingUsed, ''

class BasicAuthContentFetcher(ContentFetcher):
    def __init__(self, url, username, password, encoding=None):
        super(BasicAuthContentFetcher, self).__init__(url, encoding=encoding)
        self.username = username
        self.password = password

    def authenticate(self, req):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  'Basic %s' % base64string
        req.add_header('Authorization', authheader)

