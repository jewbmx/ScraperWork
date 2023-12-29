# -*- coding: utf-8 -*-

import re

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
#from resources.lib.modules import log_utils


class source:
    def __init__(self):
        try:
            self.results = []
            self.domains = ['watchseries1.video']
            self.base_link = 'https://watchseries1.video'
            self.search_link = '/search/%s'
            self.movie_link = '/movies/%s/'
            self.tvshow_link = '/tv-series/%s-season-%s-episode-%s/'
            self.cookie = client.request(self.base_link, output='cookie', timeout='5')
        except:
            #log_utils.log('__init__', 1)
            return


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year}
        url = urlencode(url)
        return url


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'year': year}
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
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            season, episode = (data['season'], data['episode']) if 'tvshowtitle' in data else ('0', '0')
            ### Swap to coded url due to a search problem lol...
            #search_title = cleantitle.get_dash(title)
            #check_term = '%s (%s)' % (title, data['year'])
            #check_title = cleantitle.get(title) if 'tvshowtitle' in data else cleantitle.get(check_term)
            #check = 'TV' if 'tvshowtitle' in data else data['year']
            #search_link = self.base_link + self.search_link % search_title
            #html = client.request(search_link, cookie=self.cookie)
            #results = client_utils.parseDOM(html, 'div', attrs={'class': 'flw-item'})
            #if 'tvshowtitle' in data:
                #regex = '<span class="float-right fdi-type">(.+?)</span>'
            #else:
                #regex = '>(\d{4})</span>'
            #results = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'a', ret='title'), re.findall(regex, i)) for i in results]
            #results = [(i[0][0], i[1][0], i[2][0]) for i in results if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            #result_url = [i[0] for i in results if check_title == cleantitle.get(i[1]) and check == i[2]][0]
            #if 'tvshowtitle' in data:
                #result_url = result_url[:-1]
                #result_url = result_url + '-season-%s-episode-%s/' % (season, episode)
            ###-------------------###
            search_title = cleantitle.geturl(title)
            if 'tvshowtitle' in data:
                result_url = self.base_link + self.tvshow_link % (search_title, season, episode)
            else:
                result_url = self.base_link + self.movie_link % search_title
            ### Ends Here.
            
            html = client.request(result_url, cookie=self.cookie)
            try:
                links = client_utils.parseDOM(html, 'iframe', ret='src')
                for link in links:
                    try:
                        for source in scrape_sources.process(hostDict, link):
                            if scrape_sources.check_host_limit(source['source'], self.results):
                                continue
                            self.results.append(source)
                    except:
                        #log_utils.log('sources', 1)
                        pass
            except:
                #log_utils.log('sources', 1)
                pass
            try:
                ext_links = client_utils.parseDOM(html, 'ul', attrs={'id': 'videolinks'})[0]
                links = client_utils.parseDOM(ext_links, 'a', ret='href')
                for link in links:
                    try:
                        link = self.base_link + link
                        host = re.findall('/open/link/.+?/(.+?)/', link)[0]
                        item = scrape_sources.make_item(hostDict, link, host=host, info=None, prep=True)
                        if item:
                            if scrape_sources.check_host_limit(item['source'], self.results):
                                continue
                            self.results.append(item)
                    except:
                        #log_utils.log('sources', 1)
                        pass
            except:
                #log_utils.log('sources', 1)
                pass
            return self.results
        except:
            #log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        if any(x in url for x in self.domains):
            try:
                html = client.request(url, cookie=self.cookie)
                try:
                    link = client_utils.parseDOM(html, 'iframe', ret='src')[0]
                    return link
                except:
                    match = re.compile(r'"(/open/site/.+?)"', re.I|re.S).findall(html)[0]
                    link = self.base_link + match
                    link = client.request(link, output='geturl')
                return link
            except:
                #log_utils.log('resolve', 1)
                pass
        else:
            return url


