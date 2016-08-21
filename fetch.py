import requests

def _session():
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
    return s

def fetch(url, **kwargs):
    try:
        while True:
            return _session().get(url, **kwargs)
    except requests.exceptions.ConnectionError:
        time.sleep(2)

