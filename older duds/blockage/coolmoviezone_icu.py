# -*- coding: UTF-8 -*-

import re

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import scrape_sources
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['coolmoviezone.beauty', 'coolmoviezone.bio', 'coolmoviezone.bond', 'coolmoviezone.tattoo',
            'coolmoviezone.icu', 'coolmoviezone.pics', 'coolmoviezone.homes', 'coolmoviezone.agency', 'coolmoviezone.company',
            'coolmoviezone.cfd', 'coolmoviezone.show', 'coolmoviezone.studio', 'coolmoviezone.ninja', 'coolmoviezone.online',
            'coolmoviezone.io', 'coolmoviezone.biz', 'coolmoviezone.info'
        ]
        self.base_link = 'https://coolmoviezone.beauty'
        self.search_link = '/search/%s/feed/rss2/'


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
        url = urlencode(url)
        return url


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            title = data['title']
            year = data['year']
            check_term = '%s (%s)' % (title, year)
            check_title = cleantitle.get_plus(check_term)
            search_url = self.base_link + self.search_link % cleantitle.geturl(title)
            html = client.scrapePage(search_url).text
            items = client_utils.parseDOM(html, 'item')
            r = [(client_utils.parseDOM(i, 'title'), client_utils.parseDOM(i, 'link')) for i in items]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            url = [i[1] for i in r if check_title == cleantitle.get_plus(i[0])][0]
            html = client.scrapePage(url).text
            links = re.compile('<td align="center"><strong><a href="(.+?)">', re.DOTALL).findall(html)
            for link in links:
                for source in scrape_sources.process(hostDict, link):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


