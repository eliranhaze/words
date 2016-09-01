import re

WORDFILE = 'word_list'
PRINT_WORDS = False

def _wordify(string):
    return re.sub('\W+', '', string).lower()

def get_words():
    words = [_wordify(s) for s in open(WORDFILE).read().splitlines()]
    print 'read', len(words), 'words'
    extras = []
    for word in words:
        last = word[-1]
        extras.append(word + ('ies' if last == 'y' else 's'))
        extras.append(word + ('d' if last == 'e' else 'ed'))
        extras.append(word + ('s' if last == 'e' else 'es'))
        extras.append(word + 'ly')
        extras.append(word + 'ing')
    return set(words + extras)

WORDS = get_words()

def num_words(title, text):
    text_words = [_wordify(s) for s in text.split()]
    found = [w for w in text_words if w in WORDS]

    if PRINT_WORDS:
        with open(_wordify(title).replace('www','') + '.out', 'w') as out:
            for f in found:
                out.write(f+'\n')
            out.write('\n=== TEXT ===\n')
            out.write(' '.join(text_words))

    return len(found)

