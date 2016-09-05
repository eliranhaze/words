import feedparser
import time

from bs4 import BeautifulSoup
from datetime import datetime

from fetch import fetch

class Source(object):

    def __init__(self):
        pass

    def urls(self, from_date=None):
        url_list = []
        for feed_url in self.FEEDS:
            feed = feedparser.parse(feed_url)
            url_list.extend(self._get_links(feed, from_date))
        return set(url_list)

    def _get_links(self, feed, from_date=None):
        links = []
        if feed:
            for entry in feed['entries']:
                if from_date:
                    date = datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                    if date < from_date:
                        continue
                links.append(entry['link'])
        return links

    def get_articles(self, from_date=None):
        for url in self._filter(self.urls(from_date)):
            response = fetch(url, verify=False)
            if response:
                soup = BeautifulSoup(response.content)
                title = soup.find('title').text
                yield self._trim(url), title, self.extract(soup)

    def _trim(self, url):
        return url.replace('http://','').replace('https://','')

    def extract(self, soup):
        return ''.join(p.text for p in self._main_element(soup).findAll('p') if len(p.text) > 50)

    def _main_element(self, soup):
        return soup

    def _filter(self, urls):
        return urls

    def __str__(self):
        return self.__class__.__name__

class NewYorker(Source):
    FEEDS = [
        'http://www.newyorker.com/feed/everything',
        'http://www.newyorker.com/feed/articles',
        'http://www.newyorker.com/feed/news',
        'http://www.newyorker.com/feed/culture',
        'http://www.newyorker.com/feed/humor',
        'http://www.newyorker.com/feed/books',
        'http://www.newyorker.com/feed/books/page-turner',
        'http://www.newyorker.com/feed/tech',
        'http://www.newyorker.com/feed/tech/elements',
        'http://www.newyorker.com/feed/business',
    ]

    def extract(self, soup):
        try:
            return soup.findAll('div', attrs={'class': 'articleBody'})[0].text
        except:
            return ''

class TheGuardian(Source):
    FEEDS = [
        'https://www.theguardian.com/uk/rss',
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/uk/culture/rss',
        'https://www.theguardian.com/education/rss',
        'https://www.theguardian.com/science/rss',
    ]

class NyTimes(Source):
    FEEDS = [
        'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/US.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Education.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Science.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Environment.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Space.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Health.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml',
    ]

    def _main_element(self, soup):
        try:
            return soup.findAll('article', attrs={'id': 'story'})[0]
        except:
            return soup

class NyBooks(Source):
    FEEDS = [
        'http://feeds.feedburner.com/nybooks',
    ]

    def _main_element(self, soup):
        try:
            return soup.findAll('article', attrs={'class': 'article'})[0]
        except:
            return soup

class TheAtlantic(Source):
    FEEDS = [
        'http://www.theatlantic.com/feed/all/',
        'http://www.theatlantic.com/feed/best-of/',
        'http://www.theatlantic.com/feed/channel/politics/',
        'http://www.theatlantic.com/feed/channel/entertainment/',
        'http://www.theatlantic.com/feed/channel/international/',
        'http://www.theatlantic.com/feed/channel/science/',
        'http://www.theatlantic.com/feed/channel/education/',
    ]

    def _main_element(self, soup):
        try:
            return soup.findAll('div', attrs={'class': 'article-body'})[0]
        except:
            return soup

    def _trim(self, url):
        return super(TheAtlantic, self)._trim(url).replace('/?utm_source=feed', '')

    def _filter(self, urls):
        return [u for u in urls if '/notes/' not in u]

class TheEconomist(Source):
    FEEDS = [
        'http://www.economist.com/feeds/print-sections/all/all.xml',
        'http://www.economist.com/sections/business-finance/rss.xml',
        'http://www.economist.com/sections/economics/rss.xml',
        'http://www.economist.com/sections/science-technology/rss.xml',
        'http://www.economist.com/sections/culture/rss.xml',
        'http://www.economist.com/sections/united-states/rss.xml',
        'http://www.economist.com/sections/middle-east-africa/rss.xml',
        'http://www.economist.com/sections/international/rss.xml',
    ]

    def _trim(self, url):
        return super(TheEconomist, self)._trim(url).replace('?fsrc=rss', '')

    def _filter(self, urls):
        return [u for u in urls if '/blogs/erasmus' not in u]

class _3AM(Source):
    FEEDS = [
        'http://www.3ammagazine.com/3am/feed/',
        'http://www.3ammagazine.com/3am/index/buzzwords/feed/',
        'http://www.3ammagazine.com/3am/index/interviews/feed/',
        'http://www.3ammagazine.com/3am/index/fiction/feed/',
        'http://www.3ammagazine.com/3am/index/criticism/feed/',
        'http://www.3ammagazine.com/3am/index/nonfiction/feed/',
    ]

class DailyNous(Source):
    FEEDS = [
        'http://dailynous.com/feed/',
    ]

def get_sources(sources=None):
    if sources:
        sources = [s.lower() for s in sources]
        condition = lambda cls: cls.__name__.lower() in sources
    else:
        condition = lambda cls: True
    return [s() for s in Source.__subclasses__() if condition(s)]
