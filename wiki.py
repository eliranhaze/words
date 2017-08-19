import re
import sys
from bs4 import BeautifulSoup as bs

from utils.fetch import fetch

ENDPOINT = 'https://en.wikipedia.org/wiki'
MIN_TEXT_LEN = 100

entry = sys.argv[1]
print 'looking for', entry
entry = entry.replace(' ','_')
url = '%s/%s' % (ENDPOINT, entry)
print 'fetching', url
response = fetch(url)
print 'got response'
soup = bs(response.content)

print 'parsing...'
# remove tables
[t.decompose() for t in soup.find_all('table')]

# find text
for p in soup.find(attrs={'id': 'bodyContent'}).find_all('p'):
    if len(p.text) >= MIN_TEXT_LEN:
        # remove footnotes
        text = re.sub('\[[a-z 0-9]+\]', '', p.text)
        print text
        break
