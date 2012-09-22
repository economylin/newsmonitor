# -*- coding: utf-8 -*-
import BeautifulSoup
import soupselect
from contentparser import ContentParser

def getTextFromSoapOjb(soapobj):
    if not soapobj:
        return ''
    if isinstance(soapobj, BeautifulSoup.Comment):
        return ''
    if hasattr(soapobj, 'parent') and hasattr(soapobj.parent, 'name') and soapobj.parent.name in ['style', 'script', 'head', 'title']:
        return ''

    if not hasattr(soapobj, 'contents'):
        return soapobj.string
    result = ''
    for content in soapobj.contents:
        result += ' ' + getTextFromSoapOjb(content)
    return result

'''
selector samples:
a[i@0]
[0]: a
[2:3]: a
[:3]: a
[2:]: a
[0]: div.headline&div.player img,h3 a
'''
class HtmlContentParser(ContentParser):

    def _getItem(self, soapobj, selector=None):
        item = {}
        leafobjs = []
        if selector:# Usually, it contains 'a', 'img', 'p', 'div'
            fields = selector.split(',')
            for field in fields:
                objs = soupselect.select(soapobj, field)
                if objs:
                    leafobjs.append(objs[0])
        else:# Usually, it contains a 'a' element
            leafobjs.append(soapobj)
        for leafobj in leafobjs:
            if leafobj.name == 'a' and not item.get('title'):
                title = leafobj.get('title')
                if not title:
                    title = getTextFromSoapOjb(leafobj)
                if not title:
                    continue
                title = title.strip()
                if not title:
                    continue
                item['title'] = title
                item['url'] = leafobj.get('href')
            elif leafobj.name == 'img' and not item.get('imgsrc'):
                if not leafobj.get('src'):
                    continue
                item['imgurl'] = leafobj.get('src')
                item['imgwidth'] = leafobj.get('width')
                item['imgheight'] = leafobj.get('height')
            elif not item.get('content'):
                item['content'] = getTextFromSoapOjb(leafobj)
                if item['content']:
                    item['content'] = item['content'].strip()
        return item

    def _getByCssSelector(self, soup, selector):
        items = []
        selectorpath = selector.split('&', 1)
        if len(selectorpath) > 1:
            parentselector = selectorpath[0].strip()
            childselector = selectorpath[1].strip()
            soapobjs = soupselect.select(soup, parentselector)
            for soapobj in soapobjs:
                item = self._getItem(soapobj, childselector)
                if item:
                    items.append(item)
        else:
            soapobjs = soupselect.select(soup, selector)
            for soapobj in soapobjs:
                item = self._getItem(soapobj)
                if item:
                    items.append(item)
        return items

    def parse(self, content, condition):
        items = []
        soup = BeautifulSoup.BeautifulSoup(content)
        selectors = condition['css'].split('|')
        for selector in selectors:
            selector = selector.strip()
            items.extend(self._getByCssSelector(soup, selector))
        for index, item in enumerate(items):
            item['rank'] =  index + 1
        return items

