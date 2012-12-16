# -*- coding: utf-8 -*-
import logging
from urlparse import urljoin

import lxml
import lxml.html.clean
import pyquery

from contentparser import ContentParser

def unicode2str(value):
    if not value:
        return value
    if type(value) == unicode:
        value = value.encode('utf-8','ignore')
    return value

def isExcluded(result, conditions, elementCount, elementIndex, element):
    econditions = conditions.get('exclude')
    if not econditions:
        return False
    length = econditions.get('length')
    content = element.text_content()
    if length:
        if not content or len(content.strip()) < length:
            return True
    return False

def isIncluded(result, conditions, elementCount, elementIndex, element):
    iconditions = conditions.get('include')
    if not iconditions:
        return True
    selector = unicode2str(iconditions.get('selector'))
    if selector:
        match = pyquery.PyQuery(element)(selector)
        if not match:
            return False
    return True

def isEnough(result, conditions, elementCount, elementIndex, element):
    econditions = conditions.get('enough')
    returnAll = econditions and econditions.get('all')
    if not returnAll:
        return len(result) > 0
    return elementIndex + 1 == elementCount

def fillItemByLink(element, item):
    title = element.text_content()
    if title:
        title = title.strip()
    if not title:
        title = element.get('title')
        if title:
            title = title.strip()
    if not title:# xinhuanet.com uses image to show news title
        childimg = None
        for childelement in element:
            if childelement.tag == 'img':
                childimg = childelement
                break
        if childimg is not None:
            title = childimg.get('alt')
    url = element.get('href')
    if title:
        item['title'] = title.strip()
    if url:
        item['url'] = url

def fillItemByImage(imgelement, item):
    src = imgelement.get('src')
    if src:
        item['imgurl'] =  src
    width = imgelement.get('width')
    if width:
        item['imgwidth'] =  width
    height = imgelement.get('height')
    if height:
        item['imgheight'] =  height

def fillItemByContent(element, item):
    content = element.text_content()
    if content:
        content = content.strip()
    if content:
        item['content'] = content

def getItem(element, conditions):
    criterion = conditions.get('criterion')
    item = {}
    if not criterion:
        fillItemByLink(element, item)
        return item
    urlselector = criterion.get('url')
    titleselector = criterion.get('title')
    imgselector = criterion.get('image')
    contentselector = criterion.get('content')
    linkselector = criterion.get('link')
    imgselector = criterion.get('imagelink')
    if item:
        return item
    return None

def getItems(htmlelement, selector, conditions):
    selector = unicode2str(selector)
    queryobj = pyquery.PyQuery(htmlelement)(selector)
    elements = []
    elementCount = len(queryobj)
    for elementIndex, element in enumerate(queryobj):
        if isExcluded(elements, conditions, elementCount, elementIndex, element):
            continue
        if not isIncluded(elements, conditions, elementCount, elementIndex, element):
            continue
        elements.append(element)
        if isEnough(elements, conditions, elementCount, elementIndex, element):
            break
    items = []
    cleaner = lxml.html.clean.Cleaner()
    for element in elements:
        celement = cleaner.clean_html(element)
        item = getItem(celement, conditions)
        if item:
            items.append(item)
    return items

def formatItems(baseurl, items):
    for item in items:
        url = item.get('url')
        if url:
            item['url'] = urljoin(baseurl, url)
        imgurl = item.get('imgurl')
        if imgurl:
            item['imgurl'] = urljoin(baseurl, imgurl)

class HtmlContentParser(ContentParser):

    def parse(self, baseurl, content, selector, conditions):
        if conditions is None:
            conditions = {}
        htmlelement = lxml.html.fromstring(content)
        try:
            items = getItems(htmlelement, selector, conditions)
            formatItems(baseurl, items)
        except Exception:
            items = None
            logging.exception('Error happens using selector %s.' % (selector, ))
        return items

