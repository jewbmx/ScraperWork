# -*- coding: utf-8 -*-

"""
Added this comment to explain changes made or any other info lol.
Just gotta add the same to any modified scrapers if ya wanna.
"""


import re
from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
#from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['SIMPLE DOMAIN NAME']
        self.base_link = 'Website Address'
        self.search_link = 'Search Link Used On Site'


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'aliases': aliases, 'year': year}
        url = urlencode(url)
        return url


    def sources(self, url, hostDict):
        try:
            if not url:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            title = data['title']
            year = data['year']
            search_title = cleantitle.get_plus(title)
            search_link = self.base_link + self.search_link % search_title
            r_html = client.request(search_link)
            r = client_utils.parseDOM(r_html, 'div', attrs={'class': 'ml-item'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'a', ret='oldtitle')) for i in r]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], re.findall('(.+?) [(](\d{4})[)]', i[1])) for i in r]
            r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
            r_link = [i[0] for i in r if cleantitle.match_alias(i[1][0], aliases) and cleantitle.match_year(i[1][1], year)][0]
            s_html = client.request(r_link)
            s_links = client_utils.parseDOM(s_html, 'iframe', ret='src')
            for s_link in s_links:
                #log_utils.log('Scraper Testing - s_link: ' + repr(s_link))
                for source in scrape_sources.process(hostDict, s_link):
                    self.results.append(source)
            return self.results
        except:
            #log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


