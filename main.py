import argparse
import sys

from datetime import datetime, timedelta

from sources import get_sources
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
                sys.stdout.write('got %d articles (current: %s)           \r' % (len(result), source.__class__.__name__))
                sys.stdout.flush()
            except Exception, e:
                erred.append((url, e))
    return result, erred

def write_output(result, erred):
    outfile = '%s/results_%s.out' % (OUTPUT_DIR, datetime.now().strftime('%d%m%y_%H%M'))
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
    return outfile

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', nargs='*', dest='sources')
    parser.add_argument('--hours', type=int, dest='hours')
    args = parser.parse_args()
    return args

def main():

    args = get_args()

    sources = get_sources(args.sources)
    from_date = (datetime.utcnow() - timedelta(hours=args.hours)) if args.hours else None

    print 'fetching articles'
    print 'sources: %s' % ','.join([str(s) for s in sources])
    if from_date:
        print 'since: %s utc' % from_date.strftime('%d-%m %H:%M')

    result, erred = fetch_articles(sources, from_date)

    print
    result.sort(key=lambda x: -len(x[2].found))
    outfile = write_output(result, erred)
    print 'results written to:', outfile

    if erred:
        print 'errs'
        for url, e in erred:
            print e, url 

if __name__ == '__main__':
    main()
