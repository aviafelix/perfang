#!/usr/bin/env python3
import asyncio
import datetime
import random
# NB: Don't rename file to asyncio.py!

async def my_sleep_func():
    await asyncio.sleep(random.randint(0, 5))

async def display_date(num, loop):
    end_time = loop.time() + 50.0
    while True:
        print("Loop: {} Time: {}".format(num, datetime.datetime.now()))
        if (loop.time() + 1.0) >= end_time:
            break
        await my_sleep_func()

def main():
    loop = asyncio.get_event_loop()

    asyncio.ensure_future(display_date(1, loop))
    asyncio.ensure_future(display_date(2, loop))

    loop.run_forever()

if __name__ == '__main__':
    main()
