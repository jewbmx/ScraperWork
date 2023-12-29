# -*- coding: utf-8 -*-

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import scrape_sources
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.results = []
        self.domains = ['123movies.unblockninja.com']
        self.base_link = 'https://123movies.unblockninja.com'
        self.search_link = '/search/?q=%s'
        self.notes = 'search seems to be broken and other search engines dont seem to find the site lol. can also add shows if it ever works again.'


    def movie(self, imdb, tmdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year}
        url = urlencode(url)
        return url


    def sources(self, url, hostDict):
        try:
            if url == None:
                return self.results
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['title']
            imdb = data['imdb']
            movie_title = cleantitle.get_plus(title)
            movie_link = self.base_link + self.search_link % movie_title
            results = client.request(movie_link)
            results = client_utils.parseDOM(results, 'div', attrs={'class': 'ml-item'})
            results = [(client_utils.parseDOM(i, 'a', ret='href'), client_utils.parseDOM(i, 'h2')) for i in results]
            results = [(i[0][0], client_utils.remove_codes(i[1][0])) for i in results if len(i[0]) > 0 and len(i[1]) > 0]
            result_url = [i[0] for i in results if movie_title == cleantitle.get_plus(i[1])][0]
            result_url = self.base_link + result_url
            result_html = client.request(result_url)
            #content = client_utils.parseDOM(result_html, 'div', attrs={'class': 'les-content'})
            #links = client_utils.parseDOM(content, 'a', ret='href')
            #<div class="player-list" style="display:none" data-imdb="tt9362722" data-os="https://streamvid.cc/player/u4qf6YzrQFqbSAY/"></div>
            links = client_utils.parseDOM(result_html, 'iframe', ret='src')
            for link in links:
                log_utils.log('123movies.unblockninja.com link: '+repr(link))
                if '123movie.su' in link:
                    continue
                for source in scrape_sources.process(hostDict, link):
                    self.results.append(source)
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


