#!/usr/bin/env python3

def simple_gen():
    yield "Hello"
    yield "World"

def main():
    gen = simple_gen()
    print(next(gen))
    print(next(gen))

    gen1 = simple_gen()
    gen2 = simple_gen()
    print(next(gen1))
    print(next(gen2))
    print(next(gen1))
    print(next(gen2))

if __name__ == '__main__':
    main()
