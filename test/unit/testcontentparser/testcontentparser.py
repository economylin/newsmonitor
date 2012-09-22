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

    def testBigPicture(self):
        # http://www.boston.com/bigpicture/
        content = self._loadTestData('bigpicture.htm')
        selector = {
                     'css': '[0]: div.headDiv2&h2 a,div.bpImageTop img,div.bpCaption',
                }
        parser = HtmlContentParser()
        items = parser.parse(content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://www.boston.com/bigpicture/2012/09/mali.html')
        self.assertEquals(item['imgurl'], 'http://inapcache.boston.com/universal/site_graphics/blogs/bigpicture/mali_092112/bp1.jpg')
        self.assertTrue(item['content'].startswith('People walk'))
        self.assertTrue(item['content'].endswith('(Joe Penney/Reuters)'))

    def testQq(self):
        # http://view.news.qq.com/
        content = self._loadTestData('qq.htm')
        selector = {
                     'css': '.left1&.left1pic a, .left1img img',
                }
        parser = HtmlContentParser()
        items = parser.parse(content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://view.news.qq.com/zt2012/bjd/index.htm')
        self.assertEquals(item['imgurl'], u'http://img1.gtimg.com/view/pics/hv1/112/69/1152/74926507.jpg')

    def testTianya(self):
        # http://focus.tianya.cn/
        content = self._loadTestData('tianya.htm')
        selector = {
                     'css': 'h1 a',
                }
        parser = HtmlContentParser()
        items = parser.parse(content, selector)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)

        item = items[0]
        self.assertEquals(item['url'], u'http://www.tianya.cn/publicforum/content/develop/1/1079839.shtml')


if __name__ == '__main__':
    unittest.main()

