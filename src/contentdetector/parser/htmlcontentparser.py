# -*- coding: utf-8 -*-
from contentparser import ContentParser
import lxml
import pyquery

class HtmlContentParser(ContentParser):

    def _fillItem(self, item, selectedelement):
        if selectedelement.tag == 'a' and not item.get('title') and not item.get('url'):
            title = selectedelement.text_content()
            if title:
                title = title.strip()
            if not title:
                title = selectedelement.get('title')
                if title:
                    title = title.strip()
            if not title:# xinhuanet.com uses image to show news title
                childimg = None
                for childelement in selectedelement:
                    if childelement.tag == 'img':
                        childimg = childelement
                        break
                if childimg is not None:
                    title = childimg.get('alt')
            url = selectedelement.get('href')
            if title or url:
                item['title'] = title
                item['url'] = url
        elif selectedelement.tag == 'img' and not item.get('imgsrc'):
            if selectedelement.get('src'):
                item['imgurl'] = selectedelement.get('src')
                item['imgwidth'] = selectedelement.get('width')
                item['imgheight'] = selectedelement.get('height')
        elif not item.get('content'):
            content = selectedelement.text_content()
            if content:
                content = content.strip()
            if content:
                item['content'] = content

    def _getItem(self, parentelement, selector=None):
        item = {}
        selectedelements = []
        if selector:# Usually, it contains 'a', 'img', 'p', 'div'
            fields = selector.split(',')
            for field in fields:
                objs = pyquery.PyQuery(parentelement)(field)
                if len(objs) > 0:
                    selectedelements.append(objs[0])
        else:# Usually, it contains a 'a' element
            selectedelements.append(parentelement)

        for selectedelement in selectedelements:
            self._fillItem(item, selectedelement)
        return item

    def _getByCssSelector(self, htmlelement, selector):
        items = []
        selectorpath = selector.split('&', 1)
        if len(selectorpath) > 1:
            parentselector = selectorpath[0].strip()
            childselector = selectorpath[1].strip()
            queryobj = pyquery.PyQuery(htmlelement)(parentselector)
            for htmlelement in queryobj:
                item = self._getItem(htmlelement, childselector)
                if item:
                    items.append(item)
        else:
            queryobj = pyquery.PyQuery(htmlelement)(selector)
            for htmlelement in queryobj:
                item = self._getItem(htmlelement)
                if item:
                    items.append(item)
        return items

    def parse(self, content, css):
        items = []
        htmlelement = lxml.html.fromstring(content)
        selectors = css.split('|')
        for selector in selectors:
            selector = selector.strip()
            items.extend(self._getByCssSelector(htmlelement, selector))
        for index, item in enumerate(items):
            item['rank'] =  index + 1
        return items

