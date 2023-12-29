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
        self.domains = ['vexmovies.space']
        self.base_link = 'https://vexmovies.space'
        self.search_link = '/search/%s/feed/rss2/'
        self.notes = 'Sources seem to be all youtube or gomo, might wanna toss this one in a junk folder.'


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
            imdb = data['imdb']
            search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
            html = client.request(search_url)
            items = client_utils.parseDOM(html, 'item')
            r = [(client_utils.parseDOM(i, 'title'), client_utils.parseDOM(i, 'link')) for i in items]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            url = [i[1] for i in r if cleantitle.match_alias(i[0], aliases)][0]
            html = client.request(url)
            imdb_check = re.findall(r'imdb.com/title/(.+?)/"', html)[0]
            if not imdb_check == imdb:
                return self.results
            links = client_utils.parseDOM(html, 'iframe', ret='src')
            for link in links:
                try:
                    if 'youtube.com' in link:
                        continue
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


