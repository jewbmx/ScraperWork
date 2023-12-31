# -*- coding: utf-8 -*-

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
        self.domains = ['yesmoviesgo.com']
        self.base_link = 'https://yesmoviesgo.com'
        self.search_link = '/search/%s'


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
            check = 'TV' if 'tvshowtitle' in data else year
            search_url = self.base_link + self.search_link % cleantitle.get_dash(title)
            r = client.request(search_url)
            r = client_utils.parseDOM(r, 'div', attrs={'class': 'flw-item'})
            if 'tvshowtitle' in data:
                regex = '<span class="float-right fdi-type">(.+?)</span>'
            else:
                regex = '<span class="fdi-item">(\d{4})</span>'
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'a', ret='title'), re.findall(regex, i)) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            result = [i[0] for i in r if cleantitle.match_alias(i[1], aliases) and check == i[2]][0]
            url = self.base_link + result
            if 'tvshowtitle' in data:
                html = client.request(url)
                result = client_utils.parseDOM(html, 'a', attrs={'data-number': episode, 'data-s-number': season}, ret='href')[0]
                url = self.base_link + result
            html = client.request(url)
            check_year = re.findall('Released:.+?(\d{4})', html)[0]
            check_year = cleantitle.match_year(check_year, year, data['year'])
            if not check_year:
                return self.results
            try:
                qual = client_utils.parseDOM(html, 'button', attrs={'class': 'btn btn-sm btn-quality'})[0]
            except:
                qual = ''
            links = client_utils.parseDOM(html, 'iframe', ret='src')
            for link in links:
                for source in scrape_sources.process(hostDict, link, info=qual):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


