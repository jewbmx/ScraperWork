# -*- coding: UTF-8 -*-

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import scrape_sources
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.genre_filter = ['animation', 'anime']
        self.domains = ['animeshow.tv']
        self.base_link = 'https://animeshow.tv'
        self.search_link = '/find.html?key=%s'


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
            search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
            r = client.scrapePage(search_url).text
            r = client_utils.parseDOM(r, 'div', attrs={'class': 'genres_result'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'div', attrs={'class': 'genres_result_title'}), client_utils.parseDOM(i, 'div', attrs={'class': 'genres_result_dates'})) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            url = [i[0] for i in r if cleantitle.match_alias(i[1], aliases) and cleantitle.match_year(i[2], year, data['year'])][0]
            if 'tvshowtitle' in data:
                url = url[:-1]
                url = url + '-episode-%s' % int(episode)
            mirrors = ['/', '-mirror-2/', '-mirror-3/', '-mirror-4/']
            for mirror in mirrors:
                try:
                    vurl = url + mirror
                    html = client.scrapePage(vurl).text
                    links = client_utils.parseDOM(html, 'iframe', ret='src')
                    for link in links:
                        if not 'http' in link:
                            continue
                        if 'mycrazygifts.com' in link:
                            continue
                        for source in scrape_sources.process(hostDict, link):
                            self.results.append(source)
                except:
                    pass
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


