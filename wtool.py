import argparse
import re
import requests
import sys

import words as w

wfile = w.WORDFILE

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', dest='add')
    parser.add_argument('--remove', dest='remove')
    parser.add_argument('--rank', dest='rank')
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
    response = requests.get(url)
    try:
        score = float(re.findall('pop_score_float: (\d+\.\d+)', response.content)[0])
        place = int(re.findall('actual_rank: \'(\d+)\'', response.content)[0])
        label = re.findall('label: \'([ %\w]+)', response.content)[0]
        print 'score: %.1f' % score
        print 'rank: %d' % place
        print label
    except:
        print '%r not found' % word

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
    elif args.check:
        check()
    else:
        raise ValueError('no args')

if __name__ == '__main__':
    main()
