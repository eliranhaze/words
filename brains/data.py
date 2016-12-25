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
         'http://www.newyorker.com/magazine/2016/12/19/our-automated-future',
         'http://www.newyorker.com/magazine/2016/02/29/mr-money-mustache-the-frugal-guru',

         'http://www.nybooks.com/articles/2016/05/26/our-awful-prisons-how-they-can-be-changed/',
         'http://www.nybooks.com/articles/2015/12/03/satan-salem/',
         'http://www.nybooks.com/articles/2016/08/18/mystery-of-hieronymus-bosch/',
         'http://www.nybooks.com/articles/2016/09/29/hobbes-spinoza-locke-leibniz-hume-wrestled-new/',

         'http://www.3ammagazine.com/3am/leiter-reports/',

         'http://www.theatlantic.com/education/archive/2016/08/across-the-border-and-into-school/496652/',
         'http://foreignpolicy.com/2016/11/10/the-dance-of-the-dunces-trump-clinton-election-republican-democrat/',

         'https://plato.stanford.edu/entries/self-reference/',
         'https://plato.stanford.edu/entries/truth/',
         'https://plato.stanford.edu/entries/reference/',
    ],
    0: [
         'http://www.dailymail.co.uk/news/article-4041542/Duke-Duchess-Cambridge-spend-private-Christmas-Middleton-family-joining-Queen-Sandringham.html',
         'http://www.dailymail.co.uk/news/article-4041424/It-s-Michael-CATson-Beloved-pet-Scrappy-turns-black-white-diagnosed-similar-skin-pigment-disorder-King-Pop.html',
         'http://www.dailymail.co.uk/tvshowbiz/article-4060958/Has-sherry-Kate-Garraway-accused-DRUNK-GMB-spilling-glass-water-fluffing-lines-speaking-guests.html',
         'http://www.dailymail.co.uk/debate/article-1278510/Depression-Its-just-new-trendy-illness.html',
         'http://www.dailymail.co.uk/debate/article-1220756/A-strange-lonely-troubling-death--.html',
         'http://www.dailymail.co.uk/debate/article-1224858/Yes-scientists-good-But-country-run-arrogant-gods-certainty-truly-hell-earth.html',
         'http://www.dailymail.co.uk/femail/article-3982918/A-charming-story-UK-s-popular-jewellery-brand-Pandora-went-small-family-business-11-5-BILLION-empire-celebs-t-it.html',
         'https://www.psychologytoday.com/blog/sex-murder-and-the-meaning-life/201612/does-trump-s-election-disprove-the-existence-god',
         'https://www.marxists.org/reference/subject/philosophy/works/fr/derrida.htm',
         'https://www.marxists.org/reference/subject/philosophy/works/ge/heidegge.htm',
         'http://www.whatchristianswanttoknow.com/20-inspirational-bible-verses-about-gods-love/',
         'http://www.foxnews.com/politics/2012/02/18/santorum-questions-obamas-christian-values-romneys-olympics-leadership.html',
         'http://www.foxnews.com/entertainment/2016/12/23/florida-beauty-pageant-winner-arrested-for-allegedly-beating-man-with-aluminum-baseball-bat.html',
         'http://www.ynetnews.com/articles/0,7340,L-4889175,00.html',
         'http://www.ynetnews.com/articles/0,7340,L-4895886,00.html',
         'https://www.thesun.co.uk/tvandshowbiz/2419251/strictly-come-dancing-dancer-gorka-marquez-fiancee-lauren-sheridan-split-blackpool-attack/',
         'https://www.thesun.co.uk/tvandshowbiz/2463681/katie-price-says-shell-take-legal-action-against-hotel-that-ejected-her-after-theft-of-100k-diamonds/',
         'http://www.creationism.org/english/marriage_en.htm',
         'http://liveanddare.com/contemplative-prayer-and-christian-meditation',
         'http://www.bodybuilding.com/content/layne-nortons-hard-truths-of-training-and-nutrition.html',
         'http://www.bodybuilding.com/content/6-biggest-blunders-to-avoid-while-trying-to-add-mass-offseason.html',
         'http://www.cracked.com/blog/4-ridiculously-underrated-movies-from-2016/',
         'http://www.cracked.com/article_20953_5-horrifying-ways-ex-can-ruin-your-life-with-nude-photos.html',
         'http://www.cracked.com/blog/5-things-every-snob-believes-that-are-totally-wrong/',
         'http://www.cracked.com/article_24442_6-hilariously-random-things-people-once-used-as-money.html',
         'http://www.cracked.com/blog/6-harsh-truths-that-will-make-you-better-person/',
    ],
}

TEST_SOURCES = {
    1: [
    ],
    0: [
    ],
}

MIN_TEXT_LEN = 1000

# TODO: handle file sources
def extract(html):
    soup = bs(minify_html(html))
    return ' '.join(p.text.strip() for p in soup.findAll('p') if len(p.text.strip()) > 80)

def to_text(sources):
    responses = multi_fetch(sources, timeout=240)
    texts = []
    for response in responses:
        text = extract(response.content)
        if len(text) >= MIN_TEXT_LEN:
            texts.append(extract(response.content))
        else:
            print '*** warning: text len %d<%d (url=%s) ***' % (len(text), MIN_TEXT_LEN, response.url)
    return texts

def get():
    data = []
    target = []
    for cls, sources in DATA_SOURCES.iteritems():
        for text in to_text(sources):
            data.append(text)
            target.append(cls)
    print 'got %d/%d data items' % (len(data), sum(len(sources) for sources in DATA_SOURCES.itervalues()))
    return data, target
