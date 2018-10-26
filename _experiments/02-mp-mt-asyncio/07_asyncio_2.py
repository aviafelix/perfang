#!/usr/bin/env python3
import asyncio


async def slow_operation():
    await asyncio.sleep(1)
    return 'Future is done!'

def main():
    def got_result(future):
        print(future.result())
        loop.stop()

    loop = asyncio.get_event_loop()
    task = loop.create_task(slow_operation())
    task.add_done_callback(got_result)

    loop.run_forever()

if __name__ == '__main__':
    main()
