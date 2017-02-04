import argparse
from datetime import timedelta

import words
from utils.fetch import Fetcher
from utils.minify import minify_html
from utils.text import extract_text

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

fetcher = Fetcher(cache=True, cache_ttl=timedelta(days=30), processor=minify_html)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url')
    parser.add_argument('--file', dest='file')
    parser.add_argument('--input', dest='input')
    parser.add_argument('--out', dest='out')
    parser.add_argument('--list', dest='list_words', action='store_true')
    args = parser.parse_args()
    if not args.file and not args.url and not args.input:
        print 'one of --url, --file, --input is required'
        exit()
    return args

def textify_web_content(content):
    return extract_text(html=content)

def main():

    args = get_args()
    if args.url:
        print 'fetching text from', args.url
        text = textify_web_content(fetcher.fetch(args.url, verify=False).content)
    elif args.file:
        print 'reading file', args.file
        text = open(args.file).read()
    elif args.input:
        print 'reading input'
        text = args.input
    else:
        raise ValueError('no args')

    if args.out:
        print 'with output'
        words.PRINT_WORDS = True
        words.PRINT_OUT = args.out

    report = words.full_report(text, list_words=args.list_words)
    report._print()

if __name__ == '__main__':
    main()
