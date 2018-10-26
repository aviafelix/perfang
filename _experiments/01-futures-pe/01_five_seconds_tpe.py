#!usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from time import sleep
"""
Thread Pool Executor is better suited for network operations or I/O.
"""

def return_after_5_seconds(message):
    sleep(5)
    return message+' 5 seconds'

def return_after_2_seconds(message):
    sleep(2)
    return message+' 2 seconds'

def return_after_3_seconds(message):
    sleep(3)
    return message+' 3 seconds'

def return_after_6_seconds(message):
    sleep(6)
    return message+' 6 seconds'

def main():
    pool = ThreadPoolExecutor(3)
    future1 = pool.submit(return_after_5_seconds, ('hello'))
    future2 = pool.submit(return_after_2_seconds, ('hello'))
    future3 = pool.submit(return_after_3_seconds, ('hello'))
    future4 = pool.submit(return_after_6_seconds, ('hello'))
    print("Is future1 done?", future1.done())
    print("Is future2 done?", future2.done())
    print("Is future3 done?", future3.done())
    print("Is future4 done?", future4.done())
    print("Future3 result:", future3.result())
    sleep(3)
    print("Is future2 done?", future2.done())
    sleep(2)
    print("Is future4 done?", future4.done())
    print("Future1 result:", future1.result())
    print("Future2 result:", future2.result())
    print("Future3 result:", future3.result())
    print("Future4 result:", future4.result())
    print("Is future1 done?", future1.done())
    print("Is future4 done?", future4.done())

if __name__ == '__main__':
    main()
