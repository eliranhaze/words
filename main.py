import sys

from datetime import datetime

from sources import all_sources
from words import full_report, _wordify

def make_title(title):
    max_size = 25
    title = title.replace('  ',' ').replace('  ',' ')
    if len(title) > max_size:
        title = title[:max_size-3] + '...'
    return title

def main():

    print 'fetching articles'
    result = []
    erred = []
    for source in all_sources():
        for url, title, text in source.get_articles():
            try:
                result.append((url, title, full_report(text)))
                sys.stdout.write('got %d articles (current: %s)           \r' % (len(result), source.__class__.__name__))
                sys.stdout.flush()
            except Exception, e:
                erred.append((url, e))

    print
    print 'sorting results'
    result.sort(key=lambda x: -len(x[2].found))

    print 'writing results'
    outfile = 'results_%s.out' % datetime.now().strftime('%d%m%y_%H%M')
    with open(outfile, 'w') as out:
        for url, title, report in result:
            if report.found:
                num = len(report.found)
                pct = report.found_percent
                rtime = report.reading_time
                def write(title):
                    out.write('%d %.2f %s %s %s\n' % (num, pct, rtime, make_title(title), url))
                try:
                    try:
                        write(title)
                    except UnicodeEncodeError:
                        title = ' '.join([_wordify(w) for w in title.split()])
                        write(title)
                except Exception, e:
                    erred.append((url, e))

    print 'results written to:', outfile

    if erred:
        print 'errs'
        for url, e in erred:
            print e, url 

if __name__ == '__main__':
    main()
