#!usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from time import sleep
from random import randint
"""
"""
def return_after_5_secs(num):
    sleep_time = randint(1, 5)
    sleep(sleep_time)
    return "Return of {}; time: {} seconds".format(num, sleep_time)

def main():
    pool = ThreadPoolExecutor(5)
    futures = []
    for x in range(5):
        futures.append(pool.submit(return_after_5_secs, x))

    w = wait(futures)
    print(w)
    print(w.done)
    print(w.not_done)
    for x in w.done:
        print(x.result())
    for x in w.not_done:
        print(x.result())

if __name__ == '__main__':
    main()
