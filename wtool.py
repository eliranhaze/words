import argparse
import words

wfile = words.WORDFILE

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', dest='add')
    parser.add_argument('--remove', dest='remove')
    args = parser.parse_args()
    if not args.add and not args.remove:
        print 'argument required'
        exit()
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
        return
    words.append(word)
    write_file(sorted(words))
 
def remove(word):
    words = read_file()
    if word not in words:
        print '%r does not exist' % word
        return
    words.remove(word)
    write_file(words)
    
def main():

    args = get_args()
    if args.add:
        add(args.add)
    elif args.remove:
        remove(args.remove)
    else:
        raise ValueError('no args')

if __name__ == '__main__':
    main()
