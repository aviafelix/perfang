#!/usr/bin/env python3
import threading
import time
import random

def worker(number):
    sleep = random.randrange(1, 10)
    time.sleep(sleep)
    print("I'm Worker {}, I slept for {} seconds".format(number, sleep))

def main():
    for i in range(5):
        # Concurrency:
        t = threading.Thread(target=worker, args=(i,))
        t.start()

if __name__ == '__main__':
    main()
