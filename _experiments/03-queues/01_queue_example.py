#!usr/bin/env python3
import concurrent.futures
import urllib.request
import time
import queue
"""
"""

URLS = [
    'http://physics.uniyar.ac.ru/main.php',
    'https://online.sbis.ru/',
    'https://fix-online.sbis.ru/',
    'https://test-online.sbis.ru/',
    'https://pre-test-online.sbis.ru/',
]

def feed_the_workers(spacing, q):
    """
    Simulate outside actors sending in work to do, request each url twice
    """
    for url in URLS + URLS:
        time.sleep(spacing)
        q.put(url)
        print("Queue Length:", q.qsize())
    print("I feed it!")
    return "DONE FEEDING"

def load_url(url, timeout):
    """
    Retrieve a single page and report the url and contents
    """
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        print("Loaded:", url)
        return conn.read()

def main():
    q = queue.Queue()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {
            executor.submit(feed_the_workers, 0.25, q): 'FEEDER DONE'
        }

        while future_to_url:
            print("Future to url length:", len(future_to_url))
            done, not_done = concurrent.futures.wait(
                future_to_url, timeout=0.25,
                return_when=concurrent.futures.FIRST_COMPLETED
            )

            time.sleep(1)
            while not q.empty():
                url = q.get()
                future_to_url[executor.submit(load_url, url, 60)] = url

            for future in done:
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('[DONE] %r generated an exception: %s' % (url, exc))
                else:
                    if url == 'FEEDER DONE':
                        print(data[:30])
                    else:
                        print('[DONE] %r page is %d bytes' % (data[:30], len(data)))
                del future_to_url[future]

            for future in not_done:
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('[NOT DONE] %r generated an exception: %s' % (url, exc))
                else:
                    if url == 'FEEDER DONE':
                        print(data[:30])
                    else:
                        print('[NOT DONE] %r page is %d bytes' % (data[:30], len(data)))
                del future_to_url[future]

if __name__ == '__main__':
    main()
