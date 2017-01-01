import feedparser
import re
import time

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime

from utils.fetch import fetch, multi_fetch, Fetcher
from utils.minify import minify_feed, minify_html

class Source(object):

    def __init__(self, feeds=None):
        if feeds:
            self.FEEDS = feeds

    def urls(self, from_date=None):
        url_list = []
        responses = Fetcher(cache=False).multi_fetch(self.FEEDS) # not using cache for feeds
        for response in responses:
            feed = feedparser.parse(minify_feed(response.content))
            url_list.extend(self._get_links(feed, from_date))
        return set(url_list).union(self.get_extra_urls())

    def get_extra_urls(self):
        return set()

    def _get_links(self, feed, from_date=None):
        links = []
        if feed:
            for entry in feed['entries']:
                if from_date:
                    published_parsed = entry.get('published_parsed')
                    published_date = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else None
                    if published_date and published_date < from_date:
                        continue
                links.append(entry['link'])
        return links

    def get_articles(self, from_date=None):
        urls = list(self._filter(self.urls(from_date)))
        responses = self.multiple_requests(urls)
        for response in responses:
            if response:
                content = self._extra_minify(minify_html(response.content))
                soup = BeautifulSoup(content)
                title = soup.find('title')
                yield self._trim(response.url), title.text if title else '---', self.extract(soup)

    def multiple_requests(self, urls):
        timeout = 600 # use a very large timeout to get all responses
        return multi_fetch(urls, timeout)

    def _trim(self, url):
        url = url.replace('http://','').replace('https://','')
        return re.sub('\?.*','',url)

    def _extra_minify(self, content):
        return content

    # TODO: should be in a util, since this text-extraction technique is used in several places
    def extract(self, soup):
        return ''.join(p.text for p in self._main_element(soup).findAll('p') if len(p.text) > 80)

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
        'http://www.newyorker.com/feed/collection/crime-and-punishment-in-the-archive',
        'http://www.newyorker.com/feed/collection/profiles-from-the-archive',
        'http://www.newyorker.com/feed/collection/nyc-in-the-archive',
        'http://www.newyorker.com/feed/collection/school-days-in-the-archive',
        'http://www.newyorker.com/feed/collection/creative-life-in-the-archive',
        'http://www.newyorker.com/feed/collection/love-stories-from-the-archive',
        'http://www.newyorker.com/feed/collection/directors-in-the-archive',
    ]

    def extract(self, soup):
        try:
            return soup.findAll('div', attrs={'class': 'articleBody'})[0].text
        except:
            return super(NewYorker, self).extract(soup)

    def get_extra_urls(self):
        urls = set()
        response = fetch('http://www.newyorker.com/popular', verify=False)
        soup = BeautifulSoup(response.content)
        for article in soup.findAll('article'):
            for a in article.findAll('a'):
                href = a.get('href')
                if href and 'contributors' not in href:
                    urls.add(href.replace('?intcid=popular', '?mbid=rss'))
        return urls

class TheGuardian(Source):
    FEEDS = [
        'https://www.theguardian.com/uk/rss',
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/uk/culture/rss',
        'https://www.theguardian.com/education/rss',
        'https://www.theguardian.com/science/rss',
    ]

    def _filter(self, urls):
        return [u for u in urls if '/sport/live' not in u]

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
        'http://rss.nytimes.com/services/xml/rss/nyt/Magazine.xml',
        'http://rss.nytimes.com/services/xml/rss/nyt/MostViewed.xml',
    ]

    def _main_element(self, soup):
        try:
            return soup.findAll('article', attrs={'id': 'story'})[0]
        except:
            return soup

    def _filter(self, urls):
        filtered = [
            'theater/theater-listings',
            'movies/movie-listings',
            'museum-gallery-listings',
        ]
        return [u for u in urls if all(f not in u for f in filtered)]

    def _extra_minify(self, content):
        content = re.sub('<meta [\s\S]*?>', '', content)
        content = re.sub('<link [\s\S]*?>', '', content)
        content = re.sub('<aside[\s\S]*?</aside>', '', content)
        content = re.sub('<ul[\s\S]*?</ul>', '', content)
        content = re.sub('<ol[\s\S]*?</ol>', '', content)
        content = re.sub('data-\w*-count="\d*"', ' ', content)
        return content

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
        'http://www.theatlantic.com/feed/channel/technology/',
        'http://www.theatlantic.com/feed/channel/health/',
        'http://www.theatlantic.com/feed/channel/sexes/',
        'http://www.theatlantic.com/feed/channel/international/',
        'http://www.theatlantic.com/feed/channel/national/',
        'http://www.theatlantic.com/feed/channel/science/',
        'http://www.theatlantic.com/feed/channel/education/',
        'http://www.theatlantic.com/feed/channel/news/',
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

class LondonBooks(Source):
    FEEDS = [
        'http://cdn.lrb.co.uk/feeds/lrb',
    ]

class LABooks(Source):
    FEEDS = [
        'https://lareviewofbooks.org/feed',
        'http://feeds.feedburner.com/themarginaliareview/XRIC',
        'http://avidly.lareviewofbooks.org/feed/',
        'http://philosoplant.lareviewofbooks.org/?feed=rss2',
        'http://shermanoaksreview.com/feed/',
        'http://eephusmag.com/feed/',
    ]

class WashingtonPost(Source):
    FEEDS = [
        'http://feeds.washingtonpost.com/rss/politics',
        'http://feeds.washingtonpost.com/rss/local',
        'http://feeds.washingtonpost.com/rss/national',
        'http://feeds.washingtonpost.com/rss/world', 
        'http://feeds.washingtonpost.com/rss/business',
    ]

class Aeon(Source):
    FEEDS = [
        'https://aeon.co/feed.rss',
    ]

class ScientificAmerican(Source):
    FEEDS = [
        # main
        'http://rss.sciam.com/ScientificAmerican-Global',
        'http://rss.sciam.com/basic-science',
        'http://rss.sciam.com/sciam/biology',
        'http://rss.sciam.com/sciam/climate',
        'http://rss.sciam.com/sciam/computing',
        'http://rss.sciam.com/sciam/energy-and-sustainability',
        'http://rss.sciam.com/sciam/ethics',
        'http://rss.sciam.com/sciam/evolution',
        'http://rss.sciam.com/sciam/health-and-medicine',
        'http://rss.sciam.com/sciam/math',
        'http://rss.sciam.com/sciam/mind-and-brain',
        'http://rss.sciam.com/sciam/neuroscience',
        'http://rss.sciam.com/sciam/physics',
        'http://rss.sciam.com/sciam/psychology',
        'http://rss.sciam.com/sciam/space',
        'http://rss.sciam.com/sciam/technology',
        'http://rss.sciam.com/sciam/weather',
        # blogs
        'http://rss.sciam.com/anthropology-in-practice/feed',
        'http://rss.sciam.com/beautiful-minds/feed',
        'http://rss.sciam.com/cross-check/feed',
        'http://rss.sciam.com/expeditions/feed',
        'http://rss.sciam.com/guest-blog/feed',
        'http://rss.sciam.com/illusion-chasers/feed',
        'http://rss.sciam.com/life-unbounded/feed',
        'http://rss.sciam.com/mind-guest-blog/feed',
        'http://rss.sciam.com/observations/feed',
        'http://rss.sciam.com/roots-of-unity/feed',
        'http://rss.sciam.com/rosetta-stones/feed',
    ]

def get_sources(sources=None):
    if sources:
        sources = [s.lower() for s in sources]
        condition = lambda cls: cls.__name__.lower() in sources
    else:
        condition = lambda cls: True
    return [s() for s in Source.__subclasses__() if condition(s)]
