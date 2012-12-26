# -*- coding: utf-8 -*-

import unittest
import os
from contentdetector import HtmlContentParser

class BaseTestCase(unittest.TestCase):

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return unicode(content, 'utf-8','ignore')


class TestBase(BaseTestCase):

    def setUp(self):
        pass

    def testBasicMainNoMatch(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a.notexist'

        conditions = {
            'criterion': {
                'url': 'a[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 0)

    def testBasicCriterionNoMatch(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a'

        conditions = {
            'criterion': {
                'url': 'a2[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 0)

    def testBasicUrl(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'url': 'a[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertIsNone(items[0].get('title'))

        conditions = {
            'criterion': {
                'url': 'a',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertIsNone(items[0].get('title'))

    def testBasicTitle(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'title': 'a[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('title'), '/?q=1')

        conditions = {
            'criterion': {
                'title': 'a',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('title'), 'link1')

    def testBasicContent(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'content': 'a[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('content'), '/?q=1')

        conditions = {
            'criterion': {
                'content': 'a',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('content'), 'link1')

    def testBasicImage(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'image': 'img[src]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.gif')
        self.assertIsNone(items[0].get('imgwidth'))
        self.assertIsNone(items[0].get('imgheight'))

        conditions = {
            'criterion': {
                'image': 'img',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.gif')
        self.assertEquals(items[0].get('imgwidth'), '10')
        self.assertEquals(items[0].get('imgheight'), '10')


    def testBasicLink(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'link': 'a[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertIsNone(items[0].get('title'))

        conditions = {
            'criterion': {
                'link': 'a',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertEquals(items[0].get('title'), 'link1')

    def testBasicImageLink(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div'

        conditions = {
            'criterion': {
                'imagelink': 'img[src]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.gif')
        self.assertIsNone(items[0].get('imgwidth'))
        self.assertIsNone(items[0].get('imgheight'))

        conditions = {
            'criterion': {
                'imagelink': 'img',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=2')
        self.assertEquals(items[0].get('title'), 'a title q2')
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.gif')
        self.assertEquals(items[0].get('imgwidth'), '10')
        self.assertEquals(items[0].get('imgheight'), '10')

    def testBasicSelf(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a img'

        conditions = {
            'criterion': {
                'image': 'self[src]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.gif')

    """
    For some unknown reason, this test case fails.
    "div a img" does match img element, but the element.getparent() return None.
    testBasicImageLink also use element.getparent(), but it gets valid parent.
    """
    def testBasicParent(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a img'

        conditions = {
            'criterion': {
                'url': 'parent[href]',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=2')

    def testBasicAll(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a'

        conditions = {
            'enough': {'all': True},
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 5)

    def testBasicExclude(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a'

        conditions = {
            'exclude': {
                'length': 10,
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=4')
        self.assertEquals(items[0].get('title'), 'link1234567890')

    def testBasicInclude(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a'

        conditions = {
            'include': {
                'selector': 'img',
            }
        }
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=2')
        self.assertEquals(items[0].get('title'), 'a title q2')

class TestDefault(BaseTestCase):

    def testBasicDefault(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('basic.htm')
        parser = HtmlContentParser()
        selector = 'div a'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertEquals(items[0].get('title'), 'link1')

    def testBasicDefaultImg(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('complex.htm')
        parser = HtmlContentParser()
        selector = 'div#div1 img'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertEquals(items[0].get('title'), 'img-alt')
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.jpg')

    def testBasicDefaultImgNoLink(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('complex.htm')
        parser = HtmlContentParser()
        selector = 'div#div3 img'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertIsNone(items[0].get('url'))
        self.assertEquals(items[0].get('title'), 'img-alt')
        self.assertEquals(items[0].get('imgurl'), 'http://www.google.com/1.jpg')

    def testBasicDefaultLink(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('complex.htm')
        parser = HtmlContentParser()
        selector = 'div#div1 a'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=1')
        self.assertEquals(items[0].get('title'), 'img-alt')
        self.assertIsNone(items[0].get('imgurl'))

    def testBasicDefaultLink2(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('complex.htm')
        parser = HtmlContentParser()
        selector = 'div#div2 a'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=2')
        self.assertEquals(items[0].get('title'), 'div2 link a')

    def testBasicDefaultAutoLink(self):
        url = 'http://www.google.com/'
        content = self._loadTestData('complex.htm')
        parser = HtmlContentParser()
        selector = 'div#div2'

        conditions = None
        items = parser.parse(url, content, selector, conditions)
        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].get('url'), 'http://www.google.com/?q=2')
        self.assertEquals(items[0].get('title'), 'div2 link a')

class TestSites(BaseTestCase):

    def testBigPicture(self):
        url = 'http://www.boston.com/bigpicture/'
        content = self._loadTestData('bigpicture.htm')
        parser = HtmlContentParser()
        selector = 'div.headDiv2:first'
        conditions = {
            'criterion': {
                'link': 'h2 a',
                'image': 'div.bpImageTop img',
                'content': 'div.bpCaption',
            }
        }
        items = parser.parse(url, content, selector, conditions)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['url'], u'http://www.boston.com/bigpicture/2012/09/mali.html')
        self.assertEquals(items[0]['imgurl'], 'http://inapcache.boston.com/universal/site_graphics/blogs/bigpicture/mali_092112/bp1.jpg')
        self.assertTrue(items[0]['content'].startswith('People walk'))
        self.assertTrue(items[0]['content'].endswith('(Joe Penney/Reuters)'))

    def testQq(self):
        url = 'http://view.news.qq.com/'
        content = self._loadTestData('qq.htm')
        parser = HtmlContentParser()
        selector = '.left1'
        conditions = {
            'criterion': {
                'link': '.left1pic a',
                'image': '.left1img img',
            }
        }
        items = parser.parse(url, content, selector, conditions)


        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['url'], u'http://view.news.qq.com/zt2012/bjd/index.htm')
        self.assertEquals(items[0]['imgurl'], u'http://img1.gtimg.com/view/pics/hv1/112/69/1152/74926507.jpg')
        self.assertIsNotNone(items[0]['imgwidth'])
        self.assertIsNotNone(items[0]['imgheight'])

    def testTianya(self):
        url = 'http://focus.tianya.cn/'
        content = self._loadTestData('tianya.htm')
        parser = HtmlContentParser()
        selector = 'h1 a'
        items = parser.parse(url, content, selector, None)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['url'], u'http://www.tianya.cn/publicforum/content/develop/1/1079839.shtml')

    def testXinhuanet(self):
        url = 'http://www.xinhuanet.com/'
        content = self._loadTestData('xinhuanet.htm')
        selector = '#pictt a'
        parser = HtmlContentParser()
        conditions = {
            'criterion': {
                'link': 'self',
                'title': 'img[alt]',
            }
        }
        items = parser.parse(url, content, selector, conditions)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['url'], u'http://news.xinhuanet.com/politics/2012-09/22/c_113173016.htm')
        self.assertTrue(items[0]['title'].startswith(u'网络反腐'))

    def testGovCn(self):
        url = 'http://www.gov.cn/'
        content = self._loadTestData('govcn.htm')
        selector = 'a.hei14:first'
        parser = HtmlContentParser()
        conditions = {
            'criterion': {
            }
        }
        items = parser.parse(url, content, selector, conditions)

        self.assertIsNotNone(items)
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['url'], u'http://www.gov.cn/ldhd/2012-10/01/content_2236899.htm')
        self.assertTrue(items[0]['title'].startswith(u'胡锦涛'))


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestDefault)
    # unittest.TextTestRunner().run(suite)

