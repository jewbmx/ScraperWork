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
        self.domains = ['uwatchfree.fan', 'uwatchfree.so']
        self.base_link = 'https://uwatchfree.fan'
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
            search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
            html = client.scrapePage(search_url).text
            items = client_utils.parseDOM(html, 'item')
            r = [(client_utils.parseDOM(i, 'link'), client_utils.parseDOM(i, 'title')) for i in items]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], re.findall('(.+?)(?:\((\d{4}))', i[1])) for i in r]
            r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
            url = [i[0] for i in r if cleantitle.match_alias(i[1][0], aliases) and cleantitle.match_year(i[1][1], year)][0]
            html = client.scrapePage(url).text
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


