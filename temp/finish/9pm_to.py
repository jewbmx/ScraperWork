# -*- coding: UTF-8 -*-

"""

https://9pm.to/movies/bad-boys-ride-or-die-2024
<a class="play" href="#" embedUrl="https://embed.mangavault.website/fastmedia/tt4919268">720p</a>

https://9pm.to/tv-series/ncis-los-angeles-season-12
<a class="play" href="#" embedUrl="https://embed.mangavault.website/fastmedia/tt1378167-12-8">s12e08</a>

"""

from six.moves.urllib_parse import parse_qs, urlencode

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils

DOM = client_utils.parseDOM


class source:
    def __init__(self):
        self.results = []
        self.domains = ['9pm.to']
        self.base_link = 'https://9pm.to'
        self.notes = 'Sources are "Direct Links" and seem to fail, gotta try to find whats needed for em to play.'


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
            hdlr = 'S%02dE%02d' % (int(season), int(episode)) if 'tvshowtitle' in data else year
            if 'tvshowtitle' in data:
                the_url = self.base_link + '/tv-series/%s-season-%s' % (cleantitle.geturl(title), season)
            else:
                the_url = self.base_link + '/movies/%s-%s' % (cleantitle.geturl(title), year)
            html = client.request(the_url)
            r = DOM(html, 'ul', attrs={'class': 'episodes'})[0]
            r = DOM(r, 'li')
            r = [(DOM(i, 'a', attrs={'class': 'play'}, ret='embedUrl'), DOM(i, 'a', attrs={'class': 'play'})) for i in r]
            results = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            for item in results:
                try:
                    if 'tvshowtitle' in data:
                        if not hdlr.lower() == item[1].lower():
                            continue
                        qual = '720p'
                    else:
                        qual = item[1]
                    link = item[0]
                    if not link:
                        continue
                    referrer = the_url
                    quality, info = source_utils.get_release_quality(qual, qual)
                    link += source_utils.append_headers({'Referer': referrer})
                    self.results.append({'source': 'Direct', 'quality': quality, 'info': info, 'url': link, 'direct': True})
                except:
                    log_utils.log('sources', 1)
                    pass
            return self.results
        except:
            log_utils.log('sources', 1)
            return self.results


    def resolve(self, url):
        return url


