import argparse

import words
from fetch import fetch

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url')
    parser.add_argument('--file', dest='file')
    parser.add_argument('--out', dest='out')
    args = parser.parse_args()
    if not args.file and not args.url:
        print 'either --url or --file is required'
        exit()
    return args

def main():

    args = get_args()
    if args.url:
        print 'fetching text from', args.url
        text = fetch(args.url).content
    else:
        print 'reading file', args.file
        text = open(args.file).read()

    if args.out:
        print 'with output'
        words.PRINT_WORDS = True
        words.PRINT_OUT = args.out

    report = words.full_report(text)
    report._print()

if __name__ == '__main__':
    main()