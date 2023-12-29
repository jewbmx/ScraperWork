# -*- coding: utf-8 -*-

import requests

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils
from resources.lib.modules import scrape_sources


class source:
    def __init__(self):
        try:
            self.results = []
            self.domains = ['streamm4u.com']
            self.base_link = 'https://streamm4u.com'
            self.search_link = '/search/%s'
            self.ajax_link = '/anhjax'
            self.session = requests.Session()
            self.cookie = client.request(self.base_link, output='cookie', timeout='5')
            self.notes = 'Has Shows but havent taken the time to code it in.'
        except:
            log_utils.log('__init__', 1)
            return


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        try:
            movie_title = cleantitle.geturl(title)
            check_term = '%s (%s) StreamM4u M4uFree' % (title, year)
            check_title = cleantitle.get_plus(check_term)
            search_url = self.base_link + self.search_link % movie_title
            html = client.request(search_url, cookie=self.cookie)
            r = client_utils.parseDOM(html, 'div', attrs={'class': 'col-xl-2 col-lg-3 col-md-4 col-sm-4 col-6'})
            r = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'img', ret='alt')) for i in r]
            r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            url = [i[0] for i in r if check_title == cleantitle.get_plus(i[1])][0]
            return url
        except:
            log_utils.log('movie', 1)
            return


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            html = client.request(url, cookie=self.cookie)
            post_link = self.base_link + self.ajax_link
            token = client_utils.parseDOM(html, 'meta', attrs={'name': 'csrf-token'}, ret='content')[0]
            results = client_utils.parseDOM(html, 'span', ret='data')
            for result in results:
                payload = {'url': post_link, '_token': token, 'm4u': result}
                r = self.session.post(post_link, data=payload)
                i = client_utils.replaceHTMLCodes(r.text)
                p = client_utils.parseDOM(i, 'iframe', ret='src')[0]
                for source in scrape_sources.process(hostDict, p):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


