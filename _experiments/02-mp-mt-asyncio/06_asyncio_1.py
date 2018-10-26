#!/usr/bin/env python3
import asyncio

@asyncio.coroutine
def slow_operation():
    # yield from suspends execution until
    # there's some result from asynctio.sleep

    yield from asyncio.sleep(1)

    # our task is done, here's the result
    return 'Future is done!'

def got_result(future):
    print(future.result())

def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(slow_operation())
    task.add_done_callback(got_result)
    loop.run_until_complete(task)

if __name__ == '__main__':
    main()
