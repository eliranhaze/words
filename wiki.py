import re
import sys
from bs4 import BeautifulSoup as bs

from utils.fetch import Fetcher

ENDPOINT = 'https://en.wikipedia.org/wiki'
MIN_TEXT_LEN = 100

fetcher = Fetcher(cache=False)

def _print_wrap(x, char='='):
    line = char * len(x)
    print line
    print x
    print line

entry = sys.argv[1]
print 'looking up %s...' % entry
url = '%s/%s' % (ENDPOINT, entry.replace(' ','_'))
response = fetcher.fetch(url)

if not response:
    print '%s not found' % entry
    sys.exit(-1)

soup = bs(response.content)

# remove tables
[t.decompose() for t in soup.find_all('table')]

# find title
title = soup.find(attrs={'id': 'firstHeading'}).text

# find text
for p in soup.find(attrs={'id': 'bodyContent'}).find_all('p'):
    if len(p.text) >= MIN_TEXT_LEN:
        # remove footnotes
        text = re.sub('\[[a-z 0-9]+\]', '', p.text)
        _print_wrap(title)
        print text
        break
