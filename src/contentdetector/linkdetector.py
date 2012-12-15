import lxml

def _getElementPath(element):
    result = [unicode(element.tag)]
    eid = element.get('id')
    if eid:
        result.append('<b>#' + eid + '</b>')
    eclass = element.get('class')
    if eclass:
        result.append('<b>.' + eclass.replace(' ', '.') + '</b>')
    return ''.join(result)

def _findLink(result, path, element, keyword):
    for childelement in element:
        childpath = path[:]
        childpath.append(_getElementPath(childelement))
        if childelement.tag == 'a':
            text = unicode(childelement.text_content())
            if not keyword or (text and keyword in text):
                url = childelement.get('href')
                result.append(
                    {
                        'path': ' '.join(childpath),
                        'title': text,
                        'url': url,
                    }
                )
            continue
        _findLink(result, childpath, childelement, keyword)

def detect(content, keyword):
    htmlelement = lxml.html.fromstring(content)
    result = []
    path = [_getElementPath(htmlelement)]
    _findLink(result, path, htmlelement, keyword)
    return result

