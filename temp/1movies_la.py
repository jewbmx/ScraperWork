# -*- coding: utf-8 -*-

import re
from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
#from resources.lib.modules import log_utils

DOM = client_utils.parseDOM


class source:
    def __init__(self):
        self.results = []
        self.domains = ['1movies.la']
        self.base_link = 'https://1movies.la'
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
            if not url:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            season, episode = (data['season'], data['episode']) if 'tvshowtitle' in data else ('0', '0')
            year = data['premiered'].split('-')[0] if 'tvshowtitle' in data else data['year']
            check_term = '%s - Season %s' % (title, season) if 'tvshowtitle' in data else title
            check_title = cleantitle.get(check_term)
            search_url = self.base_link + self.search_link % cleantitle.get_utf8(title)
            #log_utils.log('search_url: '+repr(search_url))
            r = client.scrapePage(search_url).text
            r = DOM(r, 'div', attrs={'class': 'ml-item'})
            #log_utils.log('r1: '+repr(r))
            r = [(DOM(i, 'a', ret='href'), DOM(i, 'a', ret='title'), re.findall(r'<h2>[(](\d{4})[)]</h2>', i)) for i in r]
            #log_utils.log('r2: '+repr(r))
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            #log_utils.log('r3: '+repr(r))
            if 'tvshowtitle' in data:
                check_season = 'season %s' % season
                result_url = [i[0] for i in r if check_title == cleantitle.get(i[1]) and i[0].startswith('/tv/')][0]
                result_link = self.base_link + result_url
            else:
                result_url = [i[0] for i in r if cleantitle.match_alias(i[1], aliases) and cleantitle.match_year(i[2], year) and i[0].startswith('/movie/')][0]
                result_link = self.base_link + result_url
            #log_utils.log('result_link: '+repr(result_link))
            r = client.scrapePage(result_link).text
            if 'tvshowtitle' in data:
                check_episode = '-season-%s-episode-%s.html' % (season, episode)
                check_episode2 = '-season-%s-episode-%02d.html' % (season, int(episode))
                r = DOM(r, 'div', attrs={'class': 'les-content'})[0]
                #log_utils.log('episode r1: '+repr(r))
                r = DOM(r, 'a', ret='href')
                #log_utils.log('episode r2: '+repr(r))
                episode_url = [i for i in r if i.endswith(check_episode) or i.endswith(check_episode2)][0]
                episode_link = self.base_link + episode_url
                #log_utils.log('episode_link: '+repr(episode_link))
                r = client.scrapePage(episode_link).text
            result_links = DOM(r, 'a', ret='data-file')
            #log_utils.log('result_links: '+repr(result_links))
            for link in result_links:
                for source in scrape_sources.process(hostDict, link):
                    self.results.append(source)
            return self.results
        except:
            #log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url

"""

result_link: 'https://1movies.la/movie/skyscraper-29241.html'
result_links: [
    'https://vidembed.cc/streaming.php?id=MjAzMDQz&title=Skyscraper&typesub=SUB&sub=L3NreXNjcmFwZXIvc2t5c2NyYXBlci52dHQ=&cover=Y292ZXIvc2t5c2NyYXBlci5wbmc=',
    'https://vidembed.cc/embedplus?id=MjAzMDQz&token=fUeGefB9u7fmDENN8kWZBw&expires=1637474076',
    'https://hydrax.net/watch?v=-eaZz-GUit',
    'https://mixdrop.co/e/mdek4zj4cxwdwvq?sub1=https://sub.movie-series.net/skyscraper/skyscraper.vtt&sub1_label=English',
    'https://sbplay1.com/e/osf1hzy7akaq?caption_1=https://sub.movie-series.net/skyscraper/skyscraper.vtt&sub_1=English',
    'https://dood.ws/e/s49d3mdgtu65?c1_file=https://sub.movie-series.net/skyscraper/skyscraper.vtt&c1_label=English'
]


episode_link: 'https://1movies.la/tv/chicago-fire-season-7-episode-5.html'
result_links: [
    'https://vidembed.io/streaming.php?id=MjUwMTMw&title=Chicago+Fire+-+Season+7+&typesub=SUB&sub=L2NoaWNhZ28tZmlyZS1zZWFzb24tNy1lcGlzb2RlLTE4LW5vLXN1Y2gtdGhpbmctYXMtYmFkLWx1Y2svY2hpY2Fnby1maXJlLXNlYXNvbi03LWVwaXNvZGUtMTgtbm8tc3VjaC10aGluZy1hcy1iYWQtbHVjay52dHQ=&cover=Y292ZXIvY2hpY2Fnby1maXJlLXNlYXNvbi03LnBuZw==',
    'https://vidembed.io/embedplus?id=MjUwMTMw&token=MxwJXlQ1FQKJysu1yxNFFQ&expires=1641439458',
    'https://hydrax.net/watch?v=Y8upBiKaa',
    'https://mixdrop.co/e/9n01m1vwtpnxxg?sub1=https://sub.movie-series.net/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck.vtt&sub1_label=English',
    'https://sbplay2.com/e/2r7jeroc5xa7?caption_1=https://sub.movie-series.net/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck.vtt&sub_1=English',
    'https://dood.ws/e/0zmxul8dr9a6?c1_file=https://sub.movie-series.net/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck/chicago-fire-season-7-episode-18-no-such-thing-as-bad-luck.vtt&c1_label=English'
]


"""
