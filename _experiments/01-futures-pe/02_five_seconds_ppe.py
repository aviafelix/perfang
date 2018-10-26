#!usr/bin/env python3
from concurrent.futures import ProcessPoolExecutor
from time import sleep
"""
Process Pool Executor is better suited for CPU intensive tasks.
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
    pool = ProcessPoolExecutor(3)
    future = pool.submit(return_after_5_seconds, ('hello'))
    future = pool.submit(return_after_2_seconds, ('hello'))
    # future = pool.submit(return_after_3_seconds, ('hello'))
    # future = pool.submit(return_after_6_seconds, ('hello'))
    print("Is future done?", future.done())
    print("Future result:", future.result())
    sleep(3)
    print("Is future done?", future.done())
    sleep(2)
    print("Is future done?", future.done())
    print("Future result:", future.result())
    print("Is future done?", future.done())

if __name__ == '__main__':
    main()
