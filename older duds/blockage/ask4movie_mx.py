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
        self.domains = ['ask4movie.net', 'ask4movie.mx']
        self.base_link = 'https://ask4movie.net'
        self.search_link = '/?s=%s'


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'aliases': aliases, 'year': year}
        url = urlencode(url)
        return url


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'aliases': aliases, 'year': year}
        url = urlencode(url)
        return url


    def episode(self, url, imdb, tmdb, tvdb, title, premiered, season, episode):
        if not url:
            return
        url = parse_qs(url)
        url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
        url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
        url = urlencode(url)
        return url


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            season, episode = (data['season'], data['episode']) if 'tvshowtitle' in data else ('0', '0')
            year = data['premiered'].split('-')[0] if 'tvshowtitle' in data else data['year']
            check_term = ('Season %s' % season) if 'tvshowtitle' in data else year
            search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
            r = client.scrapePage(search_url).text
            r = client_utils.parseDOM(r, 'div', attrs={'class': 'main-item'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'a')) for i in r]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], re.findall('(.+?)\((.+?)\)$', i[1].replace('\xa0', ''))) for i in r]
            r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
            url = [i[0] for i in r if cleantitle.match_alias(i[1][0], aliases) and i[1][1] == check_term][0]
            r = client.scrapePage(url).text
            if 'tvshowtitle' in data:
                r = client_utils.parseDOM(r, 'ul', attrs={'class': 'group-links-list'})[0]
                results = zip(client_utils.parseDOM(r, 'a', ret='data-embed-src'), client_utils.parseDOM(r, 'a'))
                links = [i[0] for i in results if i[1] == episode]
            else:
                links = client_utils.parseDOM(r, 'iframe', ret='src')
                links += client_utils.parseDOM(r, 'iframe', ret='data-src') # might not be used anymore but feelin lazy.
            for link in links:
                try:
                    for source in scrape_sources.process(hostDict, link):
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


