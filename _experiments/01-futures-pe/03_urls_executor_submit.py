#!usr/bin/env python3
import concurrent.futures
import urllib.request
"""
"""

URLS = [
    'http://physics.uniyar.ac.ru/main.php',
    'https://online.sbis.ru/',
    'https://fix-online.sbis.ru/',
    'https://test-online.sbis.ru/',
    'https://pre-test-online.sbis.ru/',
]

def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

def main():
    # Use a `with` statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(load_url, url, 10): url for url in URLS
        }
        # The `as_completed()` function takes an iterable of `Future` objects
        # and starts yielding values as soon as the futures start resolving.
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r page is %d bytes' % (url, len(data)))

if __name__ == '__main__':
    main()
