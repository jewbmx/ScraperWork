# -*- coding: UTF-8 -*-

import re
import base64

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import scrape_sources
#from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['moviesonline.fm'] # moviesonline.mx  moviesonline.la  moviesonline.mn
        self.base_link = 'https://moviesonline.fm'
        self.search_link = '/search-movies/%s.html'


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
            search_term = '%s Season %s' % (title, season) if 'tvshowtitle' in data else title
            search_url = self.base_link + self.search_link % cleantitle.get_plus(search_term)
            html = client.scrapePage(search_url).text
            r = client_utils.parseDOM(html, 'div', attrs={'class': 'ml-item'})
            if not r and 'tvshowtitle' in data:
                search_url = self.base_link + self.search_link % cleantitle.get_plus(title)
                html = client.scrapePage(search_url).text
                r = client_utils.parseDOM(html, 'div', attrs={'class': 'ml-item'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), re.findall('<b>Release:\s*(\d{4})</b>', i), re.findall('<b><i>(.+?)</i></b>', i)) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            if 'tvshowtitle' in data:
                r = [(i[0], i[1], re.findall('(.+?) Season (\d+)$', client_utils.replaceHTMLCodes(i[2]))) for i in r]
                r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
                url = [i[0] for i in r if cleantitle.match_alias(i[2][0], aliases) and cleantitle.match_year(i[1], year, data['year']) and i[2][1] == season][0]
                sepi = 'season-%1d/episode-%1d.html' % (int(season), int(episode))
                r = client.scrapePage(url).text
                r = client_utils.parseDOM(r, 'div', attrs={'id': 'details'})[0]
                r = client_utils.parseDOM(r, 'a', ret='href')
                url = [i for i in r if sepi in i][0]
            else:
                r = [(i[0], i[1], re.findall('(.+?)(?:\(\d+\)|$)', client_utils.replaceHTMLCodes(i[2]))) for i in r]
                r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
                url = [i[0] for i in r if cleantitle.match_alias(i[2], aliases) and cleantitle.match_year(i[1], year)][0]
            r = client.scrapePage(url).text
            try:
                v = re.findall(r'document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                try:
                    link = client_utils.parseDOM(b64, 'iframe', ret='src')[0]
                except:
                    link = client_utils.parseDOM(b64, 'a', ret='href')[0]
                if link:
                    item = scrape_sources.make_item(hostDict, link, host=None, info=None, prep=True)
                    if item:
                        if not scrape_sources.check_host_limit(item['source'], self.results):
                            self.results.append(item)
            except:
                #log_utils.log('sources', 1)
                pass
            try:
                r = client_utils.parseDOM(r, 'div', {'class': 'server_line'})
                links = [(client_utils.parseDOM(i, 'a', ret='href')[0], client_utils.parseDOM(i, 'p', attrs={'class': 'server_servername'})[0]) for i in r]
                for link in links:
                    try:
                        host = re.sub('Server|Link\s*\d+', '', link[1]).lower()
                        host = client_utils.replaceHTMLCodes(host)
                        if not host or 'other' in host:
                            continue
                        if host == 'vip':
                            host = 'eplayvid'
                        if host == 'voesx':
                            host = 'voe'
                        if host == 'aparat':
                            host = 'wolfstream'
                        item = scrape_sources.make_item(hostDict, link[0], host=host, info=None, prep=True)
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
                r = client.scrapePage(url).text
                try:
                    v = re.findall(r'document.write\(Base64.decode\("(.+?)"\)', r)[0]
                    b64 = base64.b64decode(v)
                    b64 = ensure_text(b64, errors='ignore')
                    try:
                        url = client_utils.parseDOM(b64, 'iframe', ret='src')[0]
                    except:
                        url = client_utils.parseDOM(b64, 'a', ret='href')[0]
                except:
                    u = client_utils.parseDOM(r, 'div', attrs={'class': 'player'})
                    url = client_utils.parseDOM(u, 'a', ret='href')[0]
                url = scrape_sources.prepare_link(url)
                return url
            except:
                #log_utils.log('resolve', 1)
                pass
        else:
            return url


