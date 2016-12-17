import requests
from bs4 import BeautifulSoup as bs

from utils.fetch import multi_fetch
from utils.minify import minify_html

DATA_SOURCES = {
    1: [
         'http://www.newyorker.com/magazine/2008/04/21/up-and-then-down',
         'http://www.newyorker.com/magazine/2013/02/04/life-at-the-top',
         'http://www.newyorker.com/magazine/2016/08/22/the-race-for-a-zika-vaccine',
         'http://www.newyorker.com/magazine/2016/11/28/obama-reckons-with-a-trump-presidency',
         'http://www.newyorker.com/magazine/2007/04/16/the-interpreter-2',
         'http://www.newyorker.com/news/news-desk/an-american-tragedy-2',
         'http://www.newyorker.com/magazine/2016/08/29/deutsche-banks-10-billion-scandal',
         'http://www.newyorker.com/books/page-turner/nabokovs-america',
         'http://www.newyorker.com/books/page-turner/w-g-sebald-and-the-emigrants',
         'http://www.newyorker.com/magazine/2016/09/05/yuja-wang-and-the-art-of-performance',
         'http://www.newyorker.com/magazine/2016/09/26/a-decade-lived-in-the-dark',
         'http://www.newyorker.com/magazine/2016/10/31/trolls-for-trump',
         'http://www.newyorker.com/magazine/2016/11/07/the-case-against-democracy',
         'http://www.newyorker.com/magazine/2015/07/20/the-really-big-one',
         'http://www.newyorker.com/magazine/2011/08/08/the-answer-man-stephen-greenblatt',

         'http://www.nybooks.com/articles/2016/05/26/our-awful-prisons-how-they-can-be-changed/',
         'http://www.nybooks.com/articles/2015/12/03/satan-salem/',
         'http://www.nybooks.com/articles/2016/08/18/mystery-of-hieronymus-bosch/',

         'http://www.theatlantic.com/education/archive/2016/08/across-the-border-and-into-school/496652/',
         'http://foreignpolicy.com/2016/11/10/the-dance-of-the-dunces-trump-clinton-election-republican-democrat/',

         'https://plato.stanford.edu/entries/self-reference/',
         'https://plato.stanford.edu/entries/truth/',
     ],
    0: [
         'http://www.dailymail.co.uk/news/article-4041542/Duke-Duchess-Cambridge-spend-private-Christmas-Middleton-family-joining-Queen-Sandringham.html',
         'http://www.dailymail.co.uk/news/article-4041424/It-s-Michael-CATson-Beloved-pet-Scrappy-turns-black-white-diagnosed-similar-skin-pigment-disorder-King-Pop.html',
         'https://www.psychologytoday.com/blog/sex-murder-and-the-meaning-life/201612/does-trump-s-election-disprove-the-existence-god',
         'https://www.marxists.org/reference/subject/philosophy/works/fr/derrida.htm',
         'https://www.marxists.org/reference/subject/philosophy/works/ge/heidegge.htm',
         'http://www.whatchristianswanttoknow.com/20-inspirational-bible-verses-about-gods-love/',
         'http://www.wikihow.com/Behave-as-a-Princess',
         'http://www.foxnews.com/politics/2012/02/18/santorum-questions-obamas-christian-values-romneys-olympics-leadership.html',
         'http://www.ynetnews.com/articles/0,7340,L-4889175,00.html',
         'https://www.thesun.co.uk/tvandshowbiz/2419251/strictly-come-dancing-dancer-gorka-marquez-fiancee-lauren-sheridan-split-blackpool-attack/',
         'http://www.dailymail.co.uk/debate/article-1278510/Depression-Its-just-new-trendy-illness.html',
     ],
}

def extract(html):
    soup = bs(minify_html(html))
    return ''.join(p.text for p in soup.findAll('p') if len(p.text) > 50)

def to_text(sources):
    responses = multi_fetch(sources, timeout=240)
    return [extract(response.content) for response in responses]

def get():
    data = []
    target = []
    for cls, sources in DATA_SOURCES.iteritems():
        for text in to_text(sources):
            data.append(text)
            target.append(cls)
    return data, target
