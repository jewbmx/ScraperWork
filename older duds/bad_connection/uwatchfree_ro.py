# -*- coding: UTF-8 -*-

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
        self.domains = ['uwatchfreemovies.sbs', 'uwatchfree.ro']
        self.base_link = 'https://uwatchfreemovies.sbs'
        self.search_link = '/search/%s/feed/rss2/'


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
            imdb = data['imdb']
            search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
            html = client.scrapePage(search_url).text
            r = client_utils.parseDOM(html, 'item')
            r = zip(client_utils.parseDOM(r, 'link'), client_utils.parseDOM(r, 'title'))
            results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
            try:
                r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
                url = [i[0] for i in r if cleantitle.match_alias(i[1], aliases) and cleantitle.match_year(i[2], year)][0]
            except:
                url = [i[0] for i in results if cleantitle.match_alias(i[1], aliases)][0]
            html = client.scrapePage(url).text
            check_imdb = re.findall('imdb.com/title/([a-z0-9]+)/', html)[0]
            if not imdb in check_imdb:
                return self.results
            body = client_utils.parseDOM(html, 'tbody')[0]
            try:
                qual = re.findall(r'/quality/(.+?)/"', body)[0]
            except:
                qual = ''
            links = []
            links += client_utils.parseDOM(body, 'a', attrs={'target': '_blank'}, ret='href')
            links += client_utils.parseDOM(html, 'iframe', ret='data-url')
            for link in links:
                try:
                    for source in scrape_sources.process(hostDict, link, info=qual):
                        if scrape_sources.check_host_limit(source['source'], self.results):
                            continue
                        self.results.append(source)
                except:
                    #log_utils.log('sources', 1)
                    pass
            return self.results
        except:
            #log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


