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
        try:
            self.results = []
            self.domains = ['watchseriesfree.co']
            self.base_link = 'https://ww1.watchseriesfree.co'
            self.search_link = '/search.html?keyword=%s'
            self.cookie = client.request(self.base_link, output='cookie', timeout='5')
            self.notes = 'search has blockage.'
        except:
            log_utils.log('__init__', 1)
            return


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        try:
            movie_title = cleantitle.get_utf8(title)
            check_title = cleantitle.get(title)
            check_term = '%s (%s)' % (title, year)
            check_title2 = cleantitle.get(check_term)
            movie_link = self.base_link + self.search_link % movie_title
            r = client.request(movie_link, cookie=self.cookie, timeout='6')
            r = client_utils.parseDOM(r, 'li', attrs={'class': 'video-block'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'div', attrs={'class': 'home_video_title'})) for i in r]
            r = [(i[0][0], re.compile('<div>(.+?)</div>', re.DOTALL).findall(i[1][0])[0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            try:
                url = [i[0] for i in r if check_title2 == cleantitle.get(i[1])][0]
            except:
                url = [i[0] for i in r if check_title == cleantitle.get(i[1])][0]
            return url
        except:
            log_utils.log('movie', 1)
            return


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            if tvshowtitle == 'House':
                tvshowtitle = 'House M.D.'
            url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except:
            log_utils.log('tvshow', 1)
            return


    def episode(self, url, imdb, tmdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            tvshow_title = cleantitle.get_utf8(data['tvshowtitle'])
            check_title = cleantitle.get(data['tvshowtitle'])
            tvshow_link = self.base_link + self.search_link % tvshow_title
            r = client.request(tvshow_link, cookie=self.cookie, timeout='6')
            r = client_utils.parseDOM(r, 'li', attrs={'class': 'video-block'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'div', attrs={'class': 'home_video_title'})) for i in r]
            r = [(i[0][0], re.compile('<div>(.+?)</div>', re.DOTALL).findall(i[1][0])[0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            url = [i[0] for i in r if check_title in cleantitle.get(i[1]) and ('Season %s' % season) in i[1]][0]
            if url:
                url += '?episode=%01d' % int(episode)
            return url
        except:
            log_utils.log('episode', 1)
            return


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            url = [i for i in url.strip('/').split('/')][-1]
            if '?episode=' in url:
                url, episode = re.findall('(.+?)\?episode=(\d*)$', url)[0]
                url = self.base_link + '/watch/%s/0' % url
                result = client.request(url, cookie=self.cookie, timeout='6')
                r = [i for i in client_utils.parseDOM(result, 'li', attrs={'class': 'nav-item'})]
                r = [(client_utils.parseDOM(i, 'a', ret='onclick'), client_utils.parseDOM(i, 'a', attrs={'class': 'nav-link btn btn-sm btn-secondary link-item sv-14'})) for i in r]
                r = [(i[0][0], re.compile('Episode ([A-Za-z0-9]+)', re.DOTALL).findall(i[1][0])) for i in r]
                urls = [i[0] for i in r if episode in i[1]]
            else:
                url = self.base_link + '/watch/%s/0' % url
                result = client.request(url, cookie=self.cookie, timeout='6')
                r = [i for i in client_utils.parseDOM(result, 'li', attrs={'class': 'nav-item'})]
                urls = [i for i in client_utils.parseDOM(r, 'a', ret='onclick')]
            for url in urls:
                link = re.compile('''load_episode_video\(\'(.+?)'\)''', re.DOTALL).findall(url)[0]
                for source in scrape_sources.process(hostDict, link):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


