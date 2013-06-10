
import lxml
import pyquery
import urlparse

from commonutil import lxmlutil
from contentfetcher import ContentFetcher

def _detectDetailUrl(url, title):
    tried = 2
    fetcher = ContentFetcher(url,tried=tried)
    fetchResult = fetcher.fetch()
    content = fetchResult.get('content')
    if not content:
        return None
    docelement = lxml.html.fromstring(content)
    aElements = pyquery.PyQuery(docelement)('a')
    for aElement in aElements:
        if lxmlutil.getCleanText(aElement) != title:
            continue
        detailUrl = aElement.get('href')
        if detailUrl:
            detailUrl = urlparse.urljoin(url, detailUrl)
            return detailUrl
    return None

def populateDetailUrls(items):
    for item in items:
        if not item.get('url'):
            continue
        if not item.get('title'):
            continue
        detailUrl = _detectDetailUrl(item['url'], item['title'])
        if detailUrl:
            item['url'] = detailUrl

