import requests
import time

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'

def fetch(url, **kwargs):
    try:
        while True:
            return session.get(url, **kwargs)
    except requests.exceptions.ConnectionError:
        time.sleep(2)
