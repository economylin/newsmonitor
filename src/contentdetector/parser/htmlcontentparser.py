# -*- coding: utf-8 -*-
import logging
import re
from urlparse import urljoin

import lxml
import lxml.html.clean
import pyquery

from contentparser import ContentParser

def getCleanText(element):
    cleaner = lxml.html.clean.Cleaner()
    celement = cleaner.clean_html(element)
    content = celement.text_content()
    if not content:
        return content
    return content.strip()

def unicode2str(value):
    if not value:
        return value
    if type(value) == unicode:
        value = value.encode('utf-8','ignore')
    return value

"""
pyquery does not work well with unicode selector
"""
def formatConditions(conditions):
    for key, value in conditions.items():
        if not isinstance(value, dict):
            continue
        for k2, v2 in value.items():
            if type(v2) != unicode:
                continue
            value[k2] = v2.encode('utf-8','ignore')

def isExcluded(result, conditions, elementCount, elementIndex, element):
    econditions = conditions.get('exclude')
    if not econditions:
        return False
    length = econditions.get('length')
    content = getCleanText(element)
    if length:
        if not content or len(content) < length:
            return True
    selector = econditions.get('selector')
    if selector:
        match = pyquery.PyQuery(element)(selector)
        if match:
            return True
    return False

def isIncluded(result, conditions, elementCount, elementIndex, element):
    iconditions = conditions.get('include')
    if not iconditions:
        return True
    selector = iconditions.get('selector')
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

def fillItemWithUrl(element, item):
    url = element.get('href')
    if url:
        item['url'] = url

def fillItemWithTitle(element, item):
    title = getCleanText(element)
    if not title:
        title = element.get('title')
        if title:
            title = title.strip()
    if title:
        item['title'] = title

def fillItemWithContent(element, item):
    content = getCleanText(element)
    if content:
        item['content'] = content

def fillItemByLink(element, item):
    title = getCleanText(element)
    if not title:
        title = element.get('title')
        if title:
            title = title.strip()
    url = element.get('href')
    if title:
        item['title'] = title
    else:
        match = pyquery.PyQuery(element)('img')
        if match:
            img = match[0]
            alt = img.get('alt')
            if alt:
                title = alt.strip()
                item['title'] = title
    if url:
        item['url'] = url

def fillItemByImage(element, item):
    src = element.get('src')
    if src:
        item['imgurl'] = src
    width = element.get('width')
    if width:
        item['imgwidth'] = width
    height = element.get('height')
    if height:
        item['imgheight'] = height

def fillItemByImageLink(element, item):
    if not item.get('title'):
        alt = element.get('alt')
        if alt:
            item['title'] = alt.strip()

    fillItemByImage(element, item)

    parent = element
    while parent is not None:
        parent = parent.getparent()
        if parent is not None and parent.tag == 'a':
            break
    if parent is not None:
        fillItemByLink(parent, item)

def getElementValue(element, selector):
    main = selector
    attr = None
    if selector.endswith(']'):
        rindex = selector.rfind('[')
        if rindex >= 0:
            main = selector[:rindex]
            attr = selector[rindex + 1:-1]
    mainElement = None
    if main == 'self':
        mainElement = element
    elif main == 'parent':
        mainElement = element.getparent()
    else:
        match = pyquery.PyQuery(element)(main)
        if match:
            mainElement = match[0]
    if mainElement is None:
        return None
    if attr:
        return mainElement.get(attr)
    return mainElement

def getItem(element, conditions):
    criterion = conditions.get('criterion')
    item = {}
    if not criterion:
        if element.tag == 'img':
            fillItemByImageLink(element, item)
        elif element.tag == 'a':
            fillItemByLink(element, item)
        else:
            match = pyquery.PyQuery(element)('a')
            if match:
                element = match[0]
            fillItemByLink(element, item)
        return item

    urlselector = criterion.get('url')
    if urlselector:
        urlelement = getElementValue(element, urlselector)
        if urlelement is not None:
            if isinstance(urlelement, basestring):
                item['url'] = urlelement
            else:
                fillItemWithUrl(urlelement, item)

    titleselector = criterion.get('title')
    if titleselector:
        titleelement = getElementValue(element, titleselector)
        if titleelement is not None:
            if isinstance(titleelement, basestring):
                item['title'] = titleelement
            else:
                fillItemWithTitle(titleelement, item)

    contentselector = criterion.get('content')
    if contentselector:
        contentelement = getElementValue(element, contentselector)
        if contentelement is not None:
            if isinstance(contentelement, basestring):
                item['content'] = contentelement
            else:
                fillItemWithContent(contentelement, item)

    imgselector = criterion.get('image')
    if imgselector:
        imageelement = getElementValue(element, imgselector)
        if imageelement is not None:
            if isinstance(imageelement, basestring):
                item['imgurl'] = imageelement
            else:
                fillItemByImage(imageelement, item)

    linkselector = criterion.get('link')
    if linkselector:
        linkelement = getElementValue(element, linkselector)
        if linkelement is not None:
            if isinstance(linkelement, basestring):
                item['url'] = linkelement
            else:
                fillItemByLink(linkelement, item)

    imglinkselector = criterion.get('imagelink')
    if imglinkselector:
        imglinkelement = getElementValue(element, imglinkselector)
        if imglinkelement is not None:
            if isinstance(imglinkelement, basestring):
                item['imgurl'] = imglinkelement
            else:
                fillItemByImageLink(imglinkelement, item)

    if item:
        return item
    return None

def getItems(htmlelement, selector, conditions):
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
    for element in elements:
        item = getItem(element, conditions)
        if item:
            items.append(item)
    return items

def formatValueByPattern(value, fromPattern, toFormat):
    m = re.match(fromPattern, value)
    if not m:
        return value
    try:
        return toFormat % m.groupdict()
    except Exception:
        logging.exception('pattern: %s, format: %s.' % (fromPattern, toFormat))
        return value

def formatItems(formatter, baseurl, items):
    for item in items:
        url = item.get('url')
        if url:
            url = urljoin(baseurl, url)
            if formatter and formatter.get('url'):
                urlformatter = formatter.get('url')
                fromPattern = urlformatter.get('from')
                toFormat = urlformatter.get('to')
                url = formatValueByPattern(item['url'],
                                            fromPattern, toFormat)
            item['url'] = url
        imgurl = item.get('imgurl')
        if imgurl:
            item['imgurl'] = urljoin(baseurl, imgurl)

class HtmlContentParser(ContentParser):

    def parse(self, baseurl, content, selector, conditions, formatter=None):
        selector = unicode2str(selector)
        if conditions is None:
            conditions = {}
        formatConditions(conditions)
        htmlelement = lxml.html.fromstring(content)
        try:
            items = getItems(htmlelement, selector, conditions)
            formatItems(formatter, baseurl, items)
        except Exception:
            items = None
            logging.exception('Error happens using selector %s.' % (selector, ))
        return items

