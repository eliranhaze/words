import feedparser
import json
import os
import re
import time

from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from urlparse import urlparse

from utils.fetch import fetch, Fetcher
from utils.minify import minify_feed, minify_html
from utils.text import extract_text

from utils.logger import get_logger
logger = get_logger('sources')

####################################################################################
# urls

class SourceUrls(object):

    def __init__(self, sources):
        self.sources = sources

    def get(self, from_date=None):
        if not self.sources:
            return set()
        logger.info('getting urls from %d url sources', len(self.sources))
        urls = set()
        for content in self._fetch_contents():
            urls.update(self._parse_urls(content, from_date))
        logger.info('got %d unique urls', len(urls))
        return urls

    def _fetch_contents(self):
        return [r.content for r in self.fetcher.multi_fetch(self.sources)]

    def _parse_urls(self, content, from_date=None):
        raise NotImplementedError

class FeedUrls(SourceUrls):

    fetcher = Fetcher(cache=True, cache_ttl=timedelta(hours=1), processor=minify_feed)

    def _parse_urls(self, content, from_date=None):
        urls = []
        if content:
            feed = feedparser.parse(content)
            for entry in feed['entries']:
                if from_date:
                    published_parsed = entry.get('published_parsed')
                    published_date = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else None
                    if published_date and published_date < from_date:
                        continue
                urls.append(entry['link'])
        return urls

class HtmlUrls(SourceUrls):

    fetcher = Fetcher(cache=False, processor=None)
    ignore_suffixes = [
        '.mp3',
        '.pdf',
        '.wav',
    ]

    def __init__(self, sources):
        super(HtmlUrls, self).__init__(sources)
        bases = set()
        for s in sources:
            parsed = urlparse(s)
            bases.add('%s://%s' % (parsed.scheme, parsed.netloc))
        if len(bases) == 1:
            self._base_url = bases.pop()
        else:
            self._base_url = ''
            logger.debug('could not determine base url for multiple sources')

    def _parse_urls(self, content, from_date=None):
        urls = []
        if content:
            for a in bs(content).find_all('a'):
                href = a.get('href')
                if href and not any(href.endswith(suffix) for suffix in self.ignore_suffixes):
                    urls.append(self._normalize_url(href))
        return urls

    def _normalize_url(self, url):
        url = re.sub('/$', '', url)
        if url.startswith('/'):
            url = '%s%s' % (self._base_url, url)
        return url

class BookmarksUrls(SourceUrls):

    def _fetch_contents(self):
        return [json.load(open(self.bookmarks_file))]
            
    def _parse_urls(self, content, from_date=None):
        # sources are bookmark folder names
        urls = set()
        for root in content['roots'].itervalues():
            if type(root) == dict:
                for child in root['children']:
                    if child['type'] == 'folder' and child['name'] in self.sources:
                        urls.update(bookmark['url'] for bookmark in child['children'] if bookmark.get('url'))
        return urls

    @property
    def bookmarks_file(self):
        return '%s/.config/google-chrome/Default/Bookmarks' % os.environ['HOME']

####################################################################################
# sources

class Source(object):

    FEEDS = []
    LINKS_PAGES = []
    bookmarks = []

    def __init__(self, feeds=None, links_pages=None, bookmarks=None):
        logger.info('%s: initializing source', self)
        self.html_fetcher = Fetcher(cache=True, cache_ttl=timedelta(days=365), processor=minify_html)
        if feeds:
            self.FEEDS = feeds
        if links_pages:
            self.LINKS_PAGES = links_pages
        if bookmarks:
            self.bookmarks = bookmarks

    def urls(self, from_date=None):
        urls_from_feed = FeedUrls(self.FEEDS).get(from_date=from_date)
        urls_from_html = HtmlUrls(self.LINKS_PAGES).get(from_date=from_date)
        all_urls = urls_from_feed.union(urls_from_html).union(self.get_extra_urls())
        if self.bookmarks:
            all_urls = all_urls.union(BookmarksUrls(self.bookmarks).get())
        logger.info('%s: got %d total urls: %s', self, len(all_urls), all_urls)
        return all_urls

    def get_extra_urls(self):
        return set()

    def get_articles(self, from_date=None):
        urls = list(self._filter(self.urls(from_date)))
        responses = self.html_fetcher.multi_fetch(urls)
        logger.debug('parsing articles from %d responses', len(responses))
        for response in responses:
            if response:
                logger.debug('parsing %s', response.url)
                content = self._extra_minify(response.content)
                soup = bs(content)
                title = soup.find('title')
                yield self._trim(response.url), title.text if title else '---', self.extract(soup)
        logger.debug('parsed %d articles', sum(1 for r in responses if r))

    def _trim(self, url):
        url = url.replace('http://','').replace('https://','')
        return re.sub('\?.*','',url)

    def _extra_minify(self, content):
        return content

    def extract(self, soup):
        return extract_text(element=soup)

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
        'http://www.newyorker.com/feed/magazine',
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

    def urls(self, *args, **kw):
        # some nyer urls are problematic
        urls = super(NewYorker, self).urls(*args, **kw)
        fixed_urls = []
        for url in urls:
            url = url.replace('origin.www.newyorker', 'www.newyorker')
            if url.startswith('/'):
                url = 'http://www.newyorker.com%s' % url
            fixed_urls.append(url)
        return set(fixed_urls)

    def extract(self, soup):
        try:
            return soup.findAll('div', attrs={'class': 'articleBody'})[0].text
        except:
            return super(NewYorker, self).extract(soup)

    def get_extra_urls(self):
        urls = set()
        response = fetch('http://www.newyorker.com/popular', verify=False)
        soup = bs(response.content)
        for article in soup.findAll('article'):
            for a in article.findAll('a'):
                href = a.get('href')
                if href and 'contributors' not in href:
                    urls.add(href.replace('?intcid=popular', '?mbid=rss'))
        return urls

    def _filter(self, urls):
        return [
            u for u in urls if not (
                u.startswith('http://video') or
                'cartoons/daily-cartoon/' in u or
                '.com/podcast/' in u)
        ]

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
