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

def _text_words(text):
    return [_wordify(s) for s in text.split()]

def find_words(text_words):
    return [w for w in text_words if w in WORDS]

def num_words(text, title=None):
    text_words = _text_words(text)
    found = find_words(text_words)

    if PRINT_WORDS and title:
        with open(_wordify(title).replace('www','') + '.out', 'w') as out:
            for f in found:
                out.write(f+'\n')
            out.write('\n=== TEXT ===\n')
            out.write(' '.join(text_words))

    return len(found)

def full_report(text):
    text_words = _text_words(text)
    unique_text_words = set(text_words)
    found = find_words(text_words)
    unique_found = set(found)
    return dict(
        num_text = len(text_words),
        num_unique_text = len(unique_text_words),
        num_found = len(found),
        num_unique_found = len(unique_found),
        found_percent = 100.*len(found)/len(text_words),
    )
