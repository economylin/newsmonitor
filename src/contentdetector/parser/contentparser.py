# -*- coding: utf-8 -*-
'''
;    used to separate selectors between parsers, eg 'xmlselector;cssselector'
/    used to specify xml path 
.    used to specify json selector; used to specify xml path for leaf node for xml parser
|    used to separate css selector, to extract different parts from a html page
&    used to separate leaf node from branch node selector in html parser
,    used to separate fields
:    used to separate from_field to to_field
#    used to specify element attribute
@    used to specify element index, start with 0
'''
class ContentParser(object):

    def parse(self, content, selector):
        return None

