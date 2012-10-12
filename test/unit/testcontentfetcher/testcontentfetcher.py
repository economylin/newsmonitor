# -*- coding: utf-8 -*-

import urllib2
import unittest
from contentdetector import ContentFetcher

class TestContentFetcher(unittest.TestCase):

    def setUp(self):
        pass
    """Proxy works as unittest.
       But it does not work when it runs on local GAE or product GAE.
    """
    def testProxy(self):
        url = 'http://www.myhttp.info/'
        req = urllib2.Request(url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1')
        handler = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
        opener = urllib2.build_opener(handler)
        res = opener.open(req, timeout=30)
        content = res.read()
        res.close()
        self.assertIsNotNone(content)

    def atestBasicFetcher(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url, timeout=10)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertEquals(url, fetchUrl)
        self.assertEquals(fetchEncoding, 'utf-8')
        self.assertIsNotNone(content)

    def btestBasicFetcherPreventCache(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url, preventCache=True, timeout=10)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertNotEquals(url, fetchUrl)
        self.assertIsNotNone(content)


if __name__ == '__main__':
    unittest.main()

