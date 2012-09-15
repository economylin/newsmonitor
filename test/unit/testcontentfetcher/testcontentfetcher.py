# -*- coding: utf-8 -*-

import unittest
from contentdetector import ContentFetcher

class TestContentFetcher(unittest.TestCase):

    def setUp(self):
        pass

    def testBasicFetcher(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertEquals(url, fetchUrl)
        self.assertEquals(fetchEncoding, 'utf-8')
        print content
        self.assertIsNotNone(content)

    def testBasicFetcherPreventCache(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url, preventCache=True)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertNotEquals(url, fetchUrl)
        print content
        self.assertIsNotNone(content)


if __name__ == '__main__':
    unittest.main()

