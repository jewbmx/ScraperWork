# -*- coding: utf-8 -*-

import re

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
from resources.lib.modules import log_utils

DOM = client_utils.parseDOM


class source:
    def __init__(self):
        self.results = []
        self.domains = ['levidia.ch']
        self.base_link = 'https://www.levidia.ch/' # / is here for lazy link making lol.
        self.search_link = 'search.php?q=%s'
        self.notes = 'sim/dupe site to goojara.to & supernova.to i think.'


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
            if not url:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            season, episode = (data['season'], data['episode']) if 'tvshowtitle' in data else ('0', '0')
            year = data['premiered'].split('-')[0] if 'tvshowtitle' in data else data['year']
            search_title = cleantitle.get_plus(title)
            search_link = self.base_link + self.search_link % search_title
            search_html = client.request(search_link)
            r = DOM(search_html, 'div', attrs={'class': 'mainlink'})
            r = [(DOM(i, 'a', ret='href'), DOM(i, 'a')) for i in r]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], re.findall('(.+?) [(](\d{4})[)]', client_utils.remove_tags(i[1]))) for i in r]
            r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
            result_url = [i[0] for i in r if cleantitle.match_alias(i[1][0], aliases) and cleantitle.match_year(i[1][1], year, data['year'])][0]
            if 'tvshowtitle' in data:
                sepi = '-s%se%s-' % (season, episode)
                url = self.base_link + result_url
                html = client.request(url)
                r = DOM(html, 'li', attrs={'class': 'mlist links'})
                r = [DOM(i, 'a', ret='href') for i in r]
                sepi_url = [i[0] for i in r if sepi in i[0]][0]
                url = self.base_link + sepi_url
            else:
                url = self.base_link + result_url
            log_utils.log('url: ' + repr(url))
            result_html = client.request(url)
            links = DOM(result_html, 'a', attrs={'target': '_blank'}, ret='href')
            for link in links:
                if 'imdb.com' in link:
                    continue
                log_utils.log('link1: ' + repr(link))
                if '/go.php' in link:
                    try:
                        link = client.request(link, output='geturl')
                    except:
                        log_utils.log('sources', 1)
                        pass
                log_utils.log('link2: ' + repr(link))
                for source in scrape_sources.process(hostDict, link):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


