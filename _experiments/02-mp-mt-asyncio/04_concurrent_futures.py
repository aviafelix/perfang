#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from time import sleep

def return_after_5_seconds(message):
    sleep(5)
    return message+' 5 seconds'

def main():
    pool = ThreadPoolExecutor(3)
    future = pool.submit(return_after_5_seconds, ("hello"))
    print(future.done())
    sleep(5)
    print(future.done())
    print(future.result())

if __name__ == '__main__':
    main()
