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
        self.domains = ['losmovies.pics', 'losmovies.online', 'losmovies.website']
        self.base_link = 'https://losmovies.pics'
        self.search_link = '/display-results?type=movies&q=%s'


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year}
        url = urlencode(url)
        return url


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'year': year}
        url = urlencode(url)
        return url


    def episode(self, url, imdb, tmdb, tvdb, title, premiered, season, episode):
        if url == None:
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
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            search_title = cleantitle.get_plus(title)
            check_title = cleantitle.get_under(title)
            check = '%s_%s' % (check_title, data['year'])
            link = self.base_link + self.search_link % search_title
            html = client.request(link)
            results = client_utils.parseDOM(html, 'div', attrs={'class': 'showRow showRowImage showRowImage'})
            results = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'img', ret='src')) for i in results]
            results = [(i[0][0], i[1][0]) for i in results if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i[0] for i in results if check in i[1]][0]
            link = self.base_link + result
            html = client.request(link)
            if 'tvshowtitle' in data:
                season = data['season']
                episode = data['episode']
                regex = '<td class="linkHidden linkHiddenUrl" data-width="700" data-height="460" data-season="%s" data-serie="%s">(.+?)</td>' % (season, episode)
                links = re.compile(regex, re.DOTALL).findall(html)
            else:
                #regex = '<td class="linkHidden linkHiddenUrl" data-width="700" data-height="460" data-season=".+?" data-serie=".+?">(.+?)</td>'
                links = client_utils.parseDOM(html, 'td', attrs={'class': 'linkHidden linkHiddenUrl'})
            for link in links:
                try:
                    if 'https://eplayvid.com/watch/%s' in link:
                        continue # this was add imdb but fails. and the sites dead with .net not working with this link either.
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


