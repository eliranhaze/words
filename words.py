import re

from brains.predict import Prediction

WORDFILE = 'wlist'
WPM = 125
MAX_WORD_REPEAT = 3

PRINT_WORDS = False
PRINT_OUT = 'words.out'

def _wordify(string, lower=True):
    w = re.sub('\W+', '', string)
    return w.lower() if lower else w

def _textify(text):
    # in the pattern '+' is not needed because of the split
    return re.sub('\W', ' ', text).lower().split()

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
        extras.append((word[:-1] if last == 'e' else word) + 'ing')
        if last == 't':
            extras.append(word[:-1] + 'ce')
        elif word[-2:] == 'ce':
            extras.append(word[:-2] + 't')
    return set(words + extras)

WORDS = get_words()

def find_words(text_words):
    found = []
    for w in text_words:
        if w in WORDS and found.count(w) < MAX_WORD_REPEAT:
            found.append(w)
    return found

def full_report(text, save=True):
    return Report(text, save)

class Report(object):

    PREDICTOR = Prediction.get()

    def __init__(self, text, save=True):
        text_words = _textify(text)
        found = find_words(text_words)
        if save:
            self.text_words = text_words
            self.unique_text_words = set(text_words)
            self.num_unique_text_words = len(self.unique_text_words)
            self.unique_found = set(found)
        self.num_text_words = len(text_words)
        self.prediction = self.predictor.predict(text)[1]
        self.found = found
        self.save = save

    @property
    def predictor(self):
        return self.PREDICTOR

    @property
    def found_percent(self):
        return 100.*len(self.found)/self.num_text_words

    @property
    def reading_minutes(self):
        return self.num_text_words * 1. / WPM

    @property
    def reading_time(self):
        m = self.reading_minutes
        #h, m = divmod(m, 60)
        #return '%dh%dm' % (h, m)
        return '%dm' % m
    
    def _print(self):
        if not self.save:
            return
        print '--- report ---'
        print '- word count: %d (%d unique)' % (self.num_text_words, self.num_unique_text_words)
        print '- found: %d (%d unique)' % (len(self.found), len(self.unique_found))
        print '- percent: %.2f%%' % self.found_percent
        print '- prediction: [%.2f]' % self.prediction
        print '- reading time: %s' % self.reading_time

        if PRINT_WORDS:
            with open(PRINT_OUT, 'w') as out:
                for f in self.found:
                    out.write(f+'\n')
                out.write('\n=== TEXT ===\n')
                out.write(' '.join(self.text_words))

