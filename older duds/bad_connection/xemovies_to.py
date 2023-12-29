# -*- coding: utf-8 -*-

import re

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['xemovie.net', 'xemovies.to', 'xemovies.net', 'xemovie.com', 'xemovie.co']
        self.base_link = 'https://xemovie.net'
        self.search_link = '/search?_token=%s&q=%s'


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
            title_cleaned = cleantitle.get_plus(title)
            r = client.scrapePage(self.base_link).text
            search_token = client_utils.parseDOM(r, 'input', attrs={'name': '_token'}, ret='value')[0]
            search_url = self.base_link + self.search_link % (search_token, title_cleaned)
            r = client.scrapePage(search_url).text
            r = client_utils.parseDOM(r, 'div', attrs={'class': 'stars col-4 col-lg-3 col-xxl-2'})
            r = [(client_utils.parseDOM(i, 'a', ret='href')[0], client_utils.parseDOM(i, 'div', attrs={'class': 'no-wrap'})[0]) for i in r]
            results = [(i[0], i[1], re.findall('(\d{4})', i[1])) for i in r]
            try:
                r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
                url = [i[0] for i in r if cleantitle.match_alias(i[1], aliases) and cleantitle.match_year(i[2], year)][0]
            except:
                url = [i[0] for i in results if cleantitle.match_alias(i[1], aliases)][0]
            if 'tvshowtitle' in data:
                url = url[:-1] if url.endswith('/') else url
                url = url + '-season-%s-episode-%s/watch' % (season, episode)
            else:
                url = url + '/watch'
            r = client.scrapePage(url).text
            sources = re.findall(r'(?:\"|\')playlist(?:\"|\'):.+?\[(.+?)\]', r, re.S)[0]
            links = re.findall(r'(?:\"|\')(?:file|src)(?:\"|\')\s*(?:\:)\s*(?:\"|\')(.+?)(?:\"|\')', sources, re.S)
            for link in links:
                try:
                    item = scrape_sources.make_direct_item(hostDict, link, host=None, info=None, referer=self.base_link, prep=True)
                    if item:
                        if not scrape_sources.check_host_limit(item['source'], self.results):
                            self.results.append(item)
                except:
                    log_utils.log('sources', 1)
                    pass
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


