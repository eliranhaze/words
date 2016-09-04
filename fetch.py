import requests
import time
import urlparse

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'

def _is_valid_url(url):
    parse = urlparse.urlparse(url)
    return parse.scheme and parse.netloc

def fetch(url, **kwargs):
    if not _is_valid_url(url):
        return
    try:
        while True:
            return session.get(url, **kwargs)
    except requests.exceptions.ConnectionError:
        time.sleep(2)
