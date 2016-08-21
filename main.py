import sys

from sources import all_sources
from words import get_words, num_words

def main():

    print 'getting words'
    words = get_words()

    print 'fetching articles'
    result = []
    erred = []
    for source in all_sources():
        for url, title, text in source.get_articles():
            try:
                result.append((url, title, num_words(words, text)))
                sys.stdout.write('got %d articles (current: %s)           \r' % (len(result), source.__class__.__name__))
                sys.stdout.flush()
            except Exception, e:
                erred.append((url, e))

    print
    print 'sorting results'
    result.sort(key=lambda x: -x[2])
    print 'RESULT'
    for url, title, num in result:
        if num > 0:
            print num, title[:20]+'.', url

    if erred:
        print 'errs'
        for url, e in erred:
            print e, url 

if __name__ == '__main__':
    main()
