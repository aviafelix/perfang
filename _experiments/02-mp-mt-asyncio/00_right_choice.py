#!/usr/bin/env python3

def right_choice(io_bound, io_very_slow):
    """
    http://masnun.rocks/2016/10/06/async-python-the-different-forms-of-concurrency/
    
    Sync: Blocking operations.
    Async: Non blocking operations.
    Concurrency: Making progress together.
    Parallelism: Making progress in parallel.
    """
    if io_bound:
        if io_very_slow:
            print("Use Asyncio")
        else:
            print("Use Threads")
    else:
        print("Use Multi Processing")

def main():
    right_choice(True, False)

if __name__ == '__main__':
    main()
