import sys

from datetime import datetime

from sources import all_sources
from words import num_words

def main():

    print 'fetching articles'
    result = []
    erred = []
    for source in all_sources():
        for url, title, text in source.get_articles():
            try:
                result.append((url, title, num_words(url, text)))
                sys.stdout.write('got %d articles (current: %s)           \r' % (len(result), source.__class__.__name__))
                sys.stdout.flush()
            except Exception, e:
                erred.append((url, e))

    print
    print 'sorting results'
    result.sort(key=lambda x: -x[2])

    print 'writing results'
    outfile = 'results_%s.out' % datetime.now().strftime('%d%m%y_%H%M')
    with open(outfile, 'w') as out:
        for url, title, num in result:
            if num > 0:
                try:
                    try:
                        out.write('%s %s %s\n' % (num, title, url))
                    except UnicodeEncodeError:
                        out.write('%s ... %s\n' % (num, url))
                except Exception, e:
                    erred.append((url, e))

    print 'results written to:', outfile

    if erred:
        print 'errs'
        for url, e in erred:
            print e, url 

if __name__ == '__main__':
    main()
