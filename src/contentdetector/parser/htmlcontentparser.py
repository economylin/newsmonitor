# -*- coding: utf-8 -*-
from urlparse import urljoin
import lxml
import lxml.html.clean
import pyquery
from contentparser import ContentParser

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
        cleaner = lxml.html.clean.Cleaner()
        parentelement = cleaner.clean_html(parentelement)
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
        if 'title' in item or 'url' in item:
            return item
        return None

    def _getByCssSelector(self, htmlelement, selector):
        requiredIndex = -1
        items = []
        if selector.startswith('['):
            found = selector.find(']', 1)
            if found >= 0:
                try:
                    requiredIndex = int(selector[1:found])
                except:
                    pass
            else:
                found = 0
            selector = selector[found + 1:]
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
        if requiredIndex >= 0:
            return items[requiredIndex:requiredIndex+1]
        return items

    def parse(self, baseurl, css, content):
        if type(css) == unicode:
            css = css.encode('utf-8','ignore')
        items = []
        htmlelement = lxml.html.fromstring(content)
        if css.endswith('@'):
            returnmultiple = True
            css = css[:-1]
        else:
            returnmultiple = False
        selectors = css.split('|')
        for selector in selectors:
            selector = selector.strip()
            items.extend(self._getByCssSelector(htmlelement, selector))
        if not returnmultiple:
            items = items[0:1]
        for index, item in enumerate(items):
            item['rank'] =  index + 1
            itemurl = item.get('url')
            if itemurl:
                item['url'] = urljoin(baseurl, itemurl)
        return items

