# -*- coding: utf-8 -*-

from commonutil import dateutil
import base64
import logging
import urllib2

class ContentFetcher(object):
    def __init__(self, url, encoding, preventCache=False):
        self.url = url
        self.encoding = encoding
        self.preventCache = preventCache

    def authenticate(self, req):        
        pass

    def fetch(self):
        fetchUrl = None
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
            res = urllib2.urlopen(req)
            content = res.read()
            res.close()
            return fetchUrl, unicode(content, self.encoding,'ignore')
        except Exception, err:
            response = 'Error on fetch data from %s:%s ' % (self.url, err)
            logging.error(response)
            return fetchUrl, None

class BasicAuthContentFetcher(ContentFetcher):
    def __init__(self, url, encoding, username, password, preventCache=False):
        super(BasicAuthContentFetcher, self).__init__(url, encoding, preventCache=preventCache)
        self.username = username
        self.password = password

    def authenticate(self, req):        
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  'Basic %s' % base64string
        req.add_header('Authorization', authheader)

