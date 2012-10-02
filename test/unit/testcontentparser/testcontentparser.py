# -*- coding: utf-8 -*-

import unittest
import os
from contentdetector import HtmlContentParser

class TestHtmlContentParser(unittest.TestCase):

    def setUp(self):
        pass

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return unicode(content, 'utf-8','ignore')

    def testBasic(self):
        url = 'http://www.googl.com/'
        content = self._loadTestData('basic.htm')

        selector = 'a'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['title'], 'link1')

        # add '@' to the end, then will return all the matched items.
        selector = 'a@'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 5)

        # use '[]' to select which item to return
        selector = '[2]a'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['title'], 'link3')

    def testBigPicture(self):
        url = 'http://www.boston.com/bigpicture/'
        content = self._loadTestData('bigpicture.htm')
        selector = 'div.headDiv2:first&h2 a,div.bpImageTop img,div.bpCaption'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://www.boston.com/bigpicture/2012/09/mali.html')
        self.assertEquals(item['imgurl'], 'http://inapcache.boston.com/universal/site_graphics/blogs/bigpicture/mali_092112/bp1.jpg')
        self.assertTrue(item['content'].startswith('People walk'))
        self.assertTrue(item['content'].endswith('(Joe Penney/Reuters)'))

    def testQq(self):
        url = 'http://view.news.qq.com/'
        content = self._loadTestData('qq.htm')
        selector = '.left1&.left1pic a, .left1img img'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://view.news.qq.com/zt2012/bjd/index.htm')
        self.assertEquals(item['imgurl'], u'http://img1.gtimg.com/view/pics/hv1/112/69/1152/74926507.jpg')
        self.assertIsNotNone(item['imgwidth'])
        self.assertIsNotNone(item['imgheight'])

    def testTianya(self):
        url = 'http://focus.tianya.cn/'
        content = self._loadTestData('tianya.htm')
        selector = 'h1 a'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://www.tianya.cn/publicforum/content/develop/1/1079839.shtml')

    def testXinhuanet(self):
        url = 'http://www.xinhuanet.com/'
        content = self._loadTestData('xinhuanet.htm')
        selector = '#pictt a'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://news.xinhuanet.com/politics/2012-09/22/c_113173016.htm')
        self.assertTrue(item['title'].startswith(u'网络反腐'))

    def testGovCn(self):
        url = 'http://www.gov.cn/'
        content = self._loadTestData('govcn.htm')
        selector = 'a.hei14:first'
        parser = HtmlContentParser()
        items = parser.parse(url, content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://www.gov.cn/ldhd/2012-10/01/content_2236899.htm')
        self.assertTrue(item['title'].startswith(u'胡锦涛'))


if __name__ == '__main__':
    unittest.main()

