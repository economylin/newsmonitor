import copy
import json
import os

from google.appengine.ext.webapp import template
import webapp2

from commonutil import jsonutil
from contentfetcher import ContentFetcher
from contentdetector import HtmlContentParser
from contentdetector import linkdetector

_DEFAULT_NEWSSOURCE = {'active': True}
class FetchPage(webapp2.RequestHandler):
    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self):
        templateValues = {
            'newssource': _DEFAULT_NEWSSOURCE,
        }
        self._render(templateValues)

    def post(self):
        action = self.request.get('action')
        keyword = self.request.get('keyword').strip()
        if action == 'JSON':
            jsonstr = self.request.get('jsonstr')
            if jsonstr:
                newssource = json.loads(jsonstr)
            else:
                newssource = _DEFAULT_NEWSSOURCE
            parsedencoding = ''
            parsedurl = ''
            content = ''
            httpheader = ''
        else:
            newssource = {}
            newssource['active'] = bool(self.request.get('active'))
            newssource['slug'] = self.request.get('slug')
            newssource['name'] = self.request.get('name')
            newssource['fetchurl'] = self.request.get('fetchurl')
            httpheader = self.request.get('httpheader')
            if httpheader:
                newssource['header'] = json.loads(httpheader)
            newssource['encoding'] = self.request.get('encoding')
            newssource['tags'] = self.request.get('tags')
            parsedencoding = self.request.get('parsedencoding')
            parsedurl = self.request.get('parsedurl')
            newssource['selector'] = self.request.get('selector').strip()

            conditions = {}
            excludelength = self.request.get('excludelength')
            if excludelength:
                excludelength = int(excludelength)
                conditions['exclude'] = {'length': excludelength}
            includeselector = self.request.get('includeselector').strip()
            if includeselector:
                conditions['include'] = {'selector': includeselector}
            enoughall = bool(self.request.get('enoughall'))
            if enoughall:
                conditions['enough'] = {'all': enoughall}
            urlselector = self.request.get('criterionurl').strip()
            titleselector = self.request.get('criteriontitle').strip()
            imgselector = self.request.get('criterionimage').strip()
            contentselector = self.request.get('criterioncontent').strip()
            linkselector = self.request.get('criterionlink').strip()
            imagelinkselector = self.request.get('criterionimagelink').strip()
            if urlselector or titleselector or imgselector or \
                contentselector or linkselector or imgselector:
                conditions['criterion'] = {
                    'url': urlselector,
                    'title': titleselector,
                    'imgse': imgselector,
                    'content': contentselector,
                    'link': linkselector,
                    'imagelink': imagelinkselector,
                }
            newssource['conditions'] = conditions

            content = self.request.get('content')
            jsonstr = jsonutil.getReadableString(newssource)

        if 'active' not in newssource:
            newssource['active'] = True

        items = []
        links = []
        selector = newssource.get('selector')
        fetchurl = newssource.get('fetchurl')

        tried = 2 # the max try count is 3
        if (not content or not selector) and fetchurl:
            fetcher = ContentFetcher(fetchurl,
                            header=newssource.get('header'),
                            encoding=newssource.get('encoding'), tried=tried
                         )
            parsedurl, parsedencoding, content = fetcher.fetch()
        if content:
            if selector:
                tnewssource = copy.copy(newssource)
                if not tnewssource.get('conditions'):
                    tnewssource['conditions'] = {}
                tnewssource['conditions']['enough'] = {'all': True}
                parser = HtmlContentParser()
                items = parser.parse(fetchurl, content, selector, tnewssource['conditions'])
            else:
                links = linkdetector.detect(content, keyword)

        if newssource.get('header'):
            httpheader = jsonutil.getReadableString(newssource['header'])

        templateValues = {
            'newssource': newssource,
            'httpheader': httpheader,
            'content': content,
            'parsedencoding': parsedencoding,
            'parsedurl': parsedurl,
            'keyword': keyword,
            'links': links,
            'items': items,
            'jsonstr': jsonstr,
        }
        self._render(templateValues)

