# -*- coding: utf-8 -*-

import re
import requests

from six import ensure_text
from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import scrape_sources
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        try:
            self.results = []
            self.domains = ['uniquestream.net', 'uniquestreaming.net']
            self.base_link = 'https://uniquestream.net'
            self.search_link = '/?s=%s'
            self.ajax_link = '/wp-admin/admin-ajax.php'
            self.session = requests.Session()
            self.notes = 'swap to "hard coded" urls since the search has blockage. now its all got blockage and the sources were not goodies.'
        except:
            log_utils.log('__init__', 1)
            return


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except:
            #log_utils.log('movie', 1)
            return


    def tvshow(self, imdb, tmdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except:
            #log_utils.log('tvshow', 1)
            return


    def episode(self, url, imdb, tmdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except:
            #log_utils.log('episode', 1)
            return


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            season, episode = (data['season'], data['episode']) if 'tvshowtitle' in data else ('0', '0')
            year = data['year']
            """
            search_title = cleantitle.get_plus(title)
            check_term = title if 'tvshowtitle' in data else '%s %s' % (title, year)
            check_title = cleantitle.get_plus(check_term)
            search_url = self.base_link + self.search_link % search_title
            html = client.request(search_url)
            results = client_utils.parseDOM(html, 'div', attrs={'class': 'result-item'})
            results = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'img', ret='alt'), client_utils.parseDOM(i, 'span', attrs={'class': 'year'})) for i in results]
            results = [(i[0][0], i[1][0], i[2][0]) for i in results if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            result_url = [i[0] for i in results if check_title == cleantitle.get_plus(i[1]) and year == i[2]][0]
            if 'tvshowtitle' in data:
                check = '-%sx%s' % (season, episode)
                html = client.request(result_url)
                results = client_utils.parseDOM(html, 'div', attrs={'class': 'episodiotitle'})
                results = [(client_utils.parseDOM(i, 'a', ret='href')) for i in results]
                result_url = [i[0] for i in results if check in i[0]][0]
            """
            ###
            title = cleantitle.get_dash(title)
            if 'tvshowtitle' in data:
                result_url = self.base_link + '/episodes/%s-season-%s-episode-%s/' % (title, season, episode)
            else:
                result_url = self.base_link + '/movies/%s-%s/' % (title, year)
            ###
            html = client.request(result_url)
            if not html:
                return self.results
            customheaders = {
                'Host': self.domains[0],
                'Accept': '*/*',
                'Origin': self.base_link,
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': client.UserAgent,
                'Referer': result_url,
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            post_link = self.base_link + self.ajax_link
            results = re.compile('''data-type=['"](.+?)['"] data-post=['"](.+?)['"] data-nume=['"](\d+)['"]>''', re.DOTALL).findall(html)
            for data_type, data_post, data_nume in results:
                try:
                    payload = {'action': 'doo_player_ajax', 'post': data_post, 'nume': data_nume, 'type': data_type}
                    r = self.session.post(post_link, headers=customheaders, data=payload)
                    i = r.json()
                    if not i['type'] == 'iframe':
                        continue
                    p = i['embed_url'].replace('\\', '')
                    link = scrape_sources.prepare_link(p)
                    if not link:
                        continue
                    valid, host = source_utils.is_host_valid(link, hostDict)
                    quality, info = source_utils.get_release_quality(link, link)
                    link += '|%s' % urlencode({'Referer': self.base_link})
                    self.results.append({'source': host, 'quality': quality, 'url': link, 'info': info, 'direct': True})
                except:
                    log_utils.log('sources', 1)
                    pass
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


