import argparse
from bs4 import BeautifulSoup

import words
from utils.fetch import fetch
from utils.minify import minify_html

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url')
    parser.add_argument('--file', dest='file')
    parser.add_argument('--out', dest='out')
    parser.add_argument('--list', dest='list_words', action='store_true')
    args = parser.parse_args()
    if not args.file and not args.url:
        print 'either --url or --file is required'
        exit()
    return args

def textify_web_content(content):
    soup = BeautifulSoup(minify_html(content))
    return ' '.join([p.text.strip() for p in soup.findAll('p') if len(p.text.strip()) > 100])

def main():

    args = get_args()
    if args.url:
        print 'fetching text from', args.url
        text = textify_web_content(fetch(args.url, verify=False).content)
    else:
        print 'reading file', args.file
        text = open(args.file).read()

    if args.out:
        print 'with output'
        words.PRINT_WORDS = True
        words.PRINT_OUT = args.out

    report = words.full_report(text, list_words=args.list_words)
    report._print()

if __name__ == '__main__':
    main()
