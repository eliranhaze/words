import argparse
import re
import sys
from bs4 import BeautifulSoup as bs, element as el
from datetime import timedelta

import words as w
from utils.fetch import Fetcher

wfile = w.WORDFILE
fetcher = Fetcher(cache=True, cache_ttl=timedelta(days=30))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', dest='add')
    parser.add_argument('--remove', dest='remove')
    parser.add_argument('--rank', dest='rank')
    parser.add_argument('--trans', dest='trans')
    parser.add_argument('--check', dest='check', action='store_true')
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error('args required')
    return args

def read_file():
    word_list = open(wfile, 'r').read().splitlines()
    print 'read %d words from %s' % (len(word_list), wfile)
    return word_list

def write_file(word_list):
    with open(wfile, 'w') as f:
        for word in word_list:
            f.write('%s\n' % word)
    print 'written %d words to %s' % (len(word_list), wfile)

def fetch(url):
    return fetcher.fetch(url).content

def add(word):
    words = read_file()
    if word in words:
        print '%r already exists' % word
        sys.exit(1)
    extras = w.get_extras(words)
    if word in extras:
        print '%r is in extras' % word
        return
    words.append(word)
    write_file(sorted(words))
 
def remove(word):
    words = read_file()
    if word not in words:
        print '%r does not exist' % word
        sys.exit(1)
    words.remove(word)
    write_file(words)

def rank(word):
    url = 'https://stats.merriam-webster.com/pop-score-redesign.php?word=%s&t=1486731097964&id=popularity-score' % word
    response = fetch(url)
    try:
        score = float(re.findall('pop_score_float: (\d+\.\d+)', response)[0])
        place = int(re.findall('actual_rank: \'(\d+)\'', response)[0])
        label = re.findall('label: \'([ %\w]+)', response)[0]
        print 'score: %.1f' % score
        print 'rank: %d' % place
        print label
    except:
        print '%r not found' % word

def trans(word):
    url = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=10217acd-6a42-413f-a9ca-7975ae89c32d' % word
    response = fetch(url)
    try:
        entries = bs(response).find_all('entry')
    except:
        print '%r not found' % word
    for entry in entries:
        _print_entry(entry)

def _print_wrap(x, char='='):
    line = char * len(x) 
    print line
    print x
    print line

def _print_entry(entry):
    _print_wrap(entry.get('id'))
    print
    fl = entry.find('fl')
    hw = entry.find('hw')
    pr = entry.find('pr')
    print ' | '.join(x.text for x in (fl, hw, pr) if x)
    for df in entry.find_all('def'):
        _print_def(df)

def dt(x):
    text = ''
    for c in x.contents:
        if type(c) == el.Tag:
            text += _extract(c)
        else:
            text += re.sub('^:', '', unicode(c))
    text += '\n'
    return text

tags = {
    'vt': lambda x: '\ndefinition [%s]\n\n' % x.text,
    'sn': lambda x: '%s%s. ' % ('' if x.text[0].isdigit() else '  ', x.text),
    'dt': dt,
    'sd': lambda x: '  -- %s: ' % x.text,
    'ss': lambda x: 'synonym: %s\n' % x.text,
    'sx': lambda x: x.text,
    'fw': lambda x: x.text,
    'vi': lambda x: '<%s>' % x.text,
}

def _extract(tag):
    return tags[tag.name](tag) if tag.name in tags else ''

def _print_def(df):
    if not df.find('vt'):
        print '\ndefinition\n'
    text = ''
    for c in df.contents:
        if type(c) == el.Tag:
            text += _extract(c)
    print text

def _print_def2(df):
    vt = df.find('vt')
    print 'definition%s' % (' [%s]' % vt.text if vt else '')
    sns = [sn.text for sn in df.find_all('sn')]
    dts = [dt.text for dt in df.find_all('dt')]
    if not sns:
        if len(dts) == 1:
            sns = ['1']
    if len(sns) != len(dts):
        print 'warning: %d sns %d dts' % (len(sns), len(dts))
        return
    for sn, dt in zip(sns, dts):
        sn = sn if sn[0].isdigit() else '  %s' % sn
        print '%s. %s' % (sn, dt)
    
def check():
    words = read_file()
    extras = set(w.get_extras(words))
    for word in words:
        if word in extras:
            print '%r is in extras' % word
    
def main():

    args = get_args()
    if args.add:
        add(args.add)
    elif args.remove:
        remove(args.remove)
    elif args.rank:
        rank(args.rank)
    elif args.trans:
        trans(args.trans)
    elif args.check:
        check()
    else:
        raise ValueError('no args')

if __name__ == '__main__':
    main()
