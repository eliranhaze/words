# -*- coding: utf-8 -*-
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
    parser.add_argument('--exists', dest='exists')
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
        sys.exit(1)
    words.append(word)
    write_file(sorted(words))
 
def remove(word):
    words = read_file()
    if word not in words:
        print '%r does not exist' % word
        sys.exit(1)
    words.remove(word)
    write_file(words)

def exists(word):
    words = w.get_words(silent=True)
    print '%r is %slisted' % (word, '' if word in words else 'un')

def rank(word):
    url = 'https://stats.merriam-webster.com/pop-score-redesign.php?word=%s&t=1486731097964&id=popularity-score' % word
    response = fetch(url)
    try:
        score = float(re.findall('pop_score_float: (\d+\.\d+)', response)[0])
        place = int(re.findall('actual_rank: \'(\d+)\'', response)[0])
        label = re.findall('label: \'([ %\w]+)', response)[0]
        _print_wrap(word)
        print 'score: %.1f' % score
        print 'rank: %d (%s)' % (place, label.lower())
    except:
        print '%r not found' % word

#######################################################################################################
# translation

def trans(word):
    url = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=10217acd-6a42-413f-a9ca-7975ae89c32d' % word
    response = fetch(url)
    soup = bs(response)
    entries = soup.find_all('entry')
    if entries:
        print
        for entry in entries:
            _print_entry(entry)
        return entries[0].get('id').split('[')[0] # main word
    else:
        print '%r not found' % word
        _print_suggestions(soup)

def _print_wrap(x, char='='):
    line = char * len(x) 
    print line
    print x
    print line

def _print_suggestions(soup):
    sugs = soup.find_all('suggestion')
    if sugs:
        print
        print 'suggestions:'
        for sug in soup.find_all('suggestion'):
            print sug.text 

def _print_entry(entry):
    _print_wrap(entry.get('id'))
    print
    fl = entry.find('fl')
    hw = entry.find('hw')
    pr = entry.find('pr')
    print ' | '.join(x.text for x in (fl, hw, pr) if x)
    for df in entry.find_all('def'):
        _print_def(df)
    _print_uros(entry)

def _print_def(df):
    if not df.find('vt'):
        print '\ndefinition\n'
    print _extract_tags(df.contents)

def _print_uros(entry):
    uros = entry.find_all('uro')
    if uros:
        for uro in uros:
            _print_uro(uro)
        print

def _print_uro(uro):
    print _extract_tags(uro.contents)

def _extract_tags(contents, else_func=None):
    text = ''
    for c in contents:
        if type(c) == el.Tag:
            text += _extract(c)
        elif else_func:
            text += else_func(c)
    return text

def dt(x):
    return '%s\n' % _extract_tags(x.contents, lambda c: c)

def sn(x):
    text = x.text
    first = text[0]
    indent = 0
    if first.isalpha():
        indent = 2
    elif first == '(':
        indent = 4
    return '%s%s. ' % (' ' * indent, text)

tags = {
    'dt': dt,
    'sn': sn,
    'vt': lambda x: '\ndefinition [%s]\n\n' % x.text,
    'sd': lambda x: '  -- %s: ' % x.text,
    'ss': lambda x: 'synonym: %s\n' % x.text,
    'sx': lambda x: '[%s]' % x.text,
    'vi': lambda x: '<%s>' % x.text,
    'fl': lambda x: ' | %s' % x.text,
    'pr': lambda x: ' | %s' % x.text,
    'fw': lambda x: '%s' % x.text,
    'ure': lambda x: u'  —%s' % x.text.replace('*',''),
    'd_link': lambda x: x.text,
}

def _extract(tag):
    return tags[tag.name](tag) if tag.name in tags else ''

#######################################################################################################

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
    elif args.check:
        check()

    main_word = None
    if args.trans:
        main_word = trans(args.trans)
    if args.rank:
        if args.trans:
            if main_word:
                rank(main_word)
        else:
            rank(args.rank)
    if args.exists:
        if args.trans:
            if main_word:
                print
                exists(main_word)
                if args.exists != main_word:
                    exists(args.exists)
        else:
            exists(args.exists)

if __name__ == '__main__':
    main()
