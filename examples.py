#!/usr/bin/env python

from fpkit import curryable, composable, printfn

def example_a():
    @curryable
    def add(a, b):
        return a + b

    @curryable
    def mult(a, b):
        return a * b

    # Currying
    x = add(3)(5)
    f1 = mult(3)
    y = f1(5)
    print (x, y) # prints (8, 15)

    # Currying and forward function composition with the >> operator
    f2 = add(1) >> mult(9) >> add(6)

    # Regular function composition with the * operator
    f3 = printfn * f2

    f3(3) # prints 4

if __name__ == '__main__':
    example_a()
