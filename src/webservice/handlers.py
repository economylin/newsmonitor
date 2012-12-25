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
            formatter = ''
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
                if 'exclude' not in conditions:
                    conditions['exclude'] = {}
                excludelength = int(excludelength)
                conditions['exclude']['length'] = excludelength
            excludeselector = self.request.get('excludeselector').strip()
            if excludeselector:
                if 'exclude' not in conditions:
                    conditions['exclude'] = {}
                conditions['exclude']['selector'] = excludeselector

            includeselector = self.request.get('includeselector').strip()
            if includeselector:
                if 'include' not in conditions:
                    conditions['include'] = {}
                conditions['include']['selector'] = includeselector
            enoughall = bool(self.request.get('enoughall'))
            if enoughall:
                conditions['enough'] = {'all': enoughall}
            urlselector = self.request.get('urlselector').strip()
            titleselector = self.request.get('titleselector').strip()
            imageselector = self.request.get('imageselector').strip()
            contentselector = self.request.get('contentselector').strip()
            linkselector = self.request.get('linkselector').strip()
            imagelinkselector = self.request.get('imagelinkselector').strip()
            if urlselector or titleselector or contentselector or \
                imageselector or linkselector or imagelinkselector:
                conditions['criterion'] = {}
                if urlselector:
                    conditions['criterion']['url'] = urlselector
                if titleselector:
                    conditions['criterion']['title'] = titleselector
                if contentselector:
                    conditions['criterion']['content'] = contentselector
                if imageselector:
                    conditions['criterion']['image'] = imageselector
                if linkselector:
                    conditions['criterion']['link'] = linkselector
                if imagelinkselector:
                    conditions['criterion']['imagelink'] = imagelinkselector
            newssource['conditions'] = conditions

            formatter = self.request.get('formatter')
            if formatter:
                newssource['formatter'] = json.loads(formatter)

            newssource['description'] = self.request.get('description').strip()

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
                tnewssource = copy.deepcopy(newssource)
                if not tnewssource.get('conditions'):
                    tnewssource['conditions'] = {}
                tnewssource['conditions']['enough'] = {'all': True}
                parser = HtmlContentParser()
                items = parser.parse(fetchurl, content, selector,
                tnewssource['conditions'], tnewssource.get('formatter'))
            else:
                links = linkdetector.detect(content, keyword)

        if newssource.get('header'):
            httpheader = jsonutil.getReadableString(newssource['header'])

        if newssource.get('formatter'):
            formatter = jsonutil.getReadableString(newssource['formatter'])

        templateValues = {
            'newssource': newssource,
            'httpheader': httpheader,
            'formatter': formatter,
            'content': content,
            'parsedencoding': parsedencoding,
            'parsedurl': parsedurl,
            'keyword': keyword,
            'links': links,
            'items': items,
            'jsonstr': jsonstr,
        }
        self._render(templateValues)

