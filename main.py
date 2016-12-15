import argparse
import sys
import time

from datetime import datetime, timedelta

from sources import get_sources, Source
from words import full_report, _wordify

OUTPUT_DIR = 'out'

def make_title(title):
    max_size = 25
    title = title.replace('  ',' ').replace('  ',' ')
    if len(title) > max_size:
        title = title[:max_size-3] + '...'
    return title

def fetch_articles(sources, from_date=None):
    result = []
    erred = []
    for source in sources:
        for url, title, text in source.get_articles(from_date):
            try:
                result.append((url, title, full_report(text, save=False)))
                sys.stdout.write('got %d articles (current: %s)           \r' % (len(result), source))
                sys.stdout.flush()
            except Exception, e:
                erred.append((url, e))
    return result, erred

def write_output(result, erred, console):
    if not console:
        outfile = '%s/results_%s.out' % (OUTPUT_DIR, datetime.now().strftime('%d%m%y_%H%M'))
        out = open(outfile, 'w')
    for url, title, report in result:
        if report.found:
            num = len(report.found)
            pct = report.found_percent
            rtime = report.reading_time
            def write(title):
                string = '%d %.2f %s %s %s' % (num, pct, rtime, make_title(title), url)
                if console:
                    print string
                else:
                    out.write('%s\n' % string)
            try:
                try:
                    write(title)
                except UnicodeEncodeError:
                    title = ' '.join([_wordify(w) for w in title.split()])
                    write(title)
            except Exception, e:
                erred.append((url, e))
    if not console:
        out.close()
        return outfile

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', nargs='*', dest='sources')
    parser.add_argument('--hours', type=int, dest='hours')
    parser.add_argument('--feed', dest='feed')
    parser.add_argument('--console', dest='console', action='store_true')
    args = parser.parse_args()
    return args

def main():

    args = get_args()

    sources = get_sources(args.sources)
    from_date = (datetime.utcnow() - timedelta(hours=args.hours)) if args.hours else None

    if args.feed:
        source_str = str(args.feed)
        sources = [Source([args.feed])]
    else:
        source_str = ','.join([str(s) for s in sources])

    print 'fetching articles'
    print 'sources: %s' % source_str
    if from_date:
        print 'since: %s utc' % from_date.strftime('%d-%m %H:%M')

    t1 = time.time()
    result, erred = fetch_articles(sources, from_date)
    print # new line needed after previous func
    print 'done fetching in %.1fs' % (time.time()-t1)

    result.sort(key=lambda x: -len(x[2].found))
    outfile = write_output(result, erred, console=args.console)
    if outfile:
        print 'results written to:', outfile

    if erred:
        print 'errs'
        for url, e in erred:
            print e, url 

if __name__ == '__main__':
    main()
