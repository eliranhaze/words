import requests
import time

from BeautifulSoup import BeautifulSoup

from fetch import fetch

class Source(object):

    def urls(self):
        feed = fetch(self.FEED_URL, verify=False)
        return self._get_links(BeautifulSoup(feed.content))

    def _get_links(self, feed_soup):
        return [a.text for a in feed_soup.findAll('guid')]

    def gen_articles(self):
        for url in self.urls():
            try:
                soup = BeautifulSoup(fetch(url, verify=False).content)
                title = soup.findAll('title')[0].text
                yield self._trim(url), title, self.extract(soup)
            except requests.exceptions.TooManyRedirects:
                time.sleep(3)

    def _trim(self, url):
        return url.replace('http://','').replace('https://','')

    def extract(self, soup):
        return ''.join(p.text for p in soup.findAll('p') if len(p.text) > 100)

class NewYorker(Source):
    FEED_URL = 'http://www.newyorker.com/feed/everything'

    def extract(self, soup):
        return soup.findAll('div', attrs={'class': 'articleBody'})[0].text

class TheGuardian(Source):
    FEED_URL = 'https://www.theguardian.com/uk/rss'

class NyTimes(Source):
    FEED_URL = 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'

class NyBooks(Source):
    FEED_URL = 'http://feeds.feedburner.com/nybooks'

class TheAtlantic(Source):
    FEED_URL = 'http://www.theatlantic.com/feed/all/'

    def _get_links(self, feed_soup):
        return [l.get('href') for l in feed_soup.findAll('link')]

    def _trim(self, url):
        return super(TheAtlantic, self)._trim(url).replace('/?utm_source=feed', '')

class TheEconomist(Source):
    FEED_URL = 'http://www.economist.com/feeds/print-sections/all/all.xml'

class _3AM(Source):
    FEED_URL = 'http://www.3ammagazine.com/3am/feed/'

class DailyNous(Source):
    FEED_URL = 'http://dailynous.com/feed/'

def all_sources():
    return [s() for s in Source.__subclasses__()]

