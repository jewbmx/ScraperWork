# -*- coding: UTF-8 -*-

import re

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['just.watchseries.video']
        self.base_link = 'https://just.watchseries.video'


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = cleantitle.geturl(tvshowtitle)
        return url


    def episode(self, url, imdb, tmdb, tvdb, title, premiered, season, episode):
        if not url:
            return
        tvshowTitle = url
        season = '%s' % int(season)
        episode = '%02d' % int(episode)
        episodeTitle = cleantitle.geturl(title)
        url = self.base_link + '/%s-%sx%s-%s' % (tvshowTitle, str(season), str(episode), episodeTitle)
        return url


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            item_page = client.request(url)
            item_table = client_utils.parseDOM(item_page, 'table', attrs={'id': 'videotable'})[0]
            item_results = client_utils.parseDOM(item_table, 'tr', attrs={'class': 'download_link.+?'})
            item_result = [(client_utils.parseDOM(i, 'a', attrs={'class': 'vtlink'}, ret='href')[0], client_utils.parseDOM(i, 'a', attrs={'class': 'vtlink'}, ret='title')[0]) for i in item_results]
            for item in item_result:
                valid, host = source_utils.is_host_valid(item[1], hostDict)
                if source_utils.host_limit == 'true' and host in str(self.results):
                    continue
                if valid:
                    link = self.base_link + item[0]
                    self.results.append({'source': host, 'quality': 'SD', 'url': link, 'direct': False})
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        try:
            item_page = client.request(url)
            item_link = client_utils.parseDOM(item_page, 'a', attrs={'rel': 'nofollow'}, ret='href')[0]
            if item_link.startswith('/external/'):
                link = self.base_link + item_link
            else:
                link = item_link
            link = client.request(link, output='geturl')
            return link
        except:
            log_utils.log('resolve', 1)
            return url


