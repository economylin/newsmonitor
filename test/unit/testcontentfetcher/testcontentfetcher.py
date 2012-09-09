# -*- coding: utf-8 -*-

import unittest
from contentfetcher import ContentFetcher

class TestContentFetcher(unittest.TestCase):

    def setUp(self):
        pass

    def testBasicFetcher(self):
        url = 'http://www.xinhua.org/'
        encoding = 'UTF-8'
        fetcher = ContentFetcher(url, encoding)
        fetchUrl, content = fetcher.fetch()
        self.assertEquals(url, fetchUrl)
        print content
        self.assertIsNotNone(content)

    def testBasicFetcherPreventCache(self):
        url = 'http://www.xinhua.org/'
        encoding = 'UTF-8'
        fetcher = ContentFetcher(url, encoding, True)
        fetchUrl, content = fetcher.fetch()
        self.assertNotEquals(url, fetchUrl)
        print content
        self.assertIsNotNone(content)


if __name__ == '__main__':
    unittest.main()

