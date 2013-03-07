# -*- coding: utf-8 -*-
import logging
import re
import urlparse

import lxml
import pyquery
from commonutil import lxmlutil

from contentparser import ContentParser

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
    content = lxmlutil.getCleanText(element)
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

def getElementValue(element, selector):
    main = selector
    attr = None
    if selector.endswith(']'):
        rindex = selector.rfind('[')
        # if '"' is found, it must be 'attr="value"' attribute selector.
        if rindex >= 0 and selector.find('"', rindex) < 0:
            main = selector[:rindex]
            attr = selector[rindex + 1:-1]
    mainElement = None
    if main == 'self':
        mainElement = element
    elif main == 'parent':
        mainElement = element.getparent()
    else:
        if attr:# element with required attribute
            main = main + '[' + attr + ']'
        match = pyquery.PyQuery(element)(main)
        if match:
            mainElement = match[0]
    if mainElement is None:
        return None
    if attr:
        value = mainElement.get(attr)
        if value:
            value = value.strip()
        return value
    return mainElement

def getValueBySelectors(element, selectors):
    result = None
    for selector in selectors:
        matched = getElementValue(element, selector)
        if matched is not None:
            if isinstance(matched, basestring):
                result = matched
            else:
                result = lxmlutil.getCleanText(matched)
        if result:
            break
    return result

def getParentLinkElement(element, selector):
    match = pyquery.PyQuery(element)(selector)
    if match:
        parent = match[0]
    else:
        parent = None
    while parent is not None:
        parent = parent.getparent()
        if parent is not None and parent.tag == 'a':
            break
    return parent

def getItem(element, conditions):
    criterion = conditions.get('criterion')
    titleSelectors = []
    urlSelectors = []
    contentSelectors = []
    imgSelectors = []
    item = {}
    if criterion:
        urlselector = criterion.get('url')
        if urlselector:
            urlSelectors.append(urlselector)
        titleselector = criterion.get('title')
        if titleselector:
            titleSelectors.append(titleselector)
        contentselector = criterion.get('content')
        if contentselector:
            contentSelectors.append(contentselector)
        imgselector = criterion.get('image')
        if imgselector:
            titleSelectors.append(imgselector + '[alt]')
            imgSelectors.append(imgselector + '[src]')
        linkselector = criterion.get('link')
        if linkselector:
            titleSelectors.append(linkselector)
            titleSelectors.append(linkselector + '[title]')
            urlSelectors.append(linkselector + '[href]')
        imglinkselector = criterion.get('imagelink')
        if imglinkselector:
            titleSelectors.append(imglinkselector + '[alt]')
            imgSelectors.append(imglinkselector + '[src]')
    else:
        if element.tag == 'img':
            titleSelectors.append('self[alt]')
            imgSelectors.append('self[src]')
        elif element.tag == 'a':
            titleSelectors.append('self')
            titleSelectors.append('self[title]')
            urlSelectors.append('self[href]')
        else:
            match = pyquery.PyQuery(element)('a')
            if match:
                element = match[0]
                titleSelectors.append('self')
                titleSelectors.append('self[title]')
                urlSelectors.append('self[href]')
    title = getValueBySelectors(element, titleSelectors)
    if title:
        item['title'] = title

    url = getValueBySelectors(element, urlSelectors)
    if url:
        item['url'] = url

    content = getValueBySelectors(element, contentSelectors)
    if content:
        item['content'] = content

    imgurl = getValueBySelectors(element, imgSelectors)
    if imgurl:
        item['img'] = {'url': imgurl}

    # hard to integrate img parent link logic as above, so hard code here
    imglinkselector = criterion and criterion.get('imagelink')
    if imglinkselector:
        parentAElement = None
        if 'title' not in item or 'url' not in item:
            parentAElement = getParentLinkElement(element, imglinkselector)
        if parentAElement is not None and 'title' not in item:
            title = getValueBySelectors(parentAElement, ['self', 'self[title]'])
            if title:
                item['title'] = title
        if parentAElement is not None and 'url' not in item:
            url = getValueBySelectors(parentAElement, ['self[href]'])
            if url:
                item['url'] = url

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
            url = urlparse.urljoin(baseurl, url)
            if formatter and formatter.get('url'):
                urlformatter = formatter.get('url')
                fromPattern = urlformatter.get('from')
                toFormat = urlformatter.get('to')
                url = formatValueByPattern(item['url'],
                                            fromPattern, toFormat)
            item['url'] = url
        img = item.get('img')
        if img and 'url' in img:
            item['img']['url'] = urlparse.urljoin(baseurl, item['img']['url'])

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

