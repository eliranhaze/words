from BeautifulSoup import BeautifulSoup
from fetch import fetch

def get_words():
    res = fetch('https://www.vocabulary.com/lists/194479/')
    soup = BeautifulSoup(res.content)
    return [a.text for a in soup.findAll('a',{'class': 'word dynamictext'})]

def num_words(words, text):
    return sum(text.count(w) for w in words)

