import re
import sys
from bs4 import BeautifulSoup as bs

from utils.fetch import fetch

ENDPOINT = 'https://en.wikipedia.org/wiki'
MIN_TEXT_LEN = 100

def _print_wrap(x, char='='):
    line = char * len(x)
    print line
    print x
    print line

entry = sys.argv[1]
print 'looking for %s...' % entry
url = '%s/%s' % (ENDPOINT, entry.replace(' ','_'))
response = fetch(url)
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
