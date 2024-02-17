from typing import *
from relation import *

# infix results are always 'value'
# positional argumnets are integers
def add_check(f:Frame) -> Iterable[None]:
    pass

# how to describe the top of the numeric tower?
def add(a, b):
    return (a + b)

relation = Simple(fixed_handlers(({'value', 0, 1}, add_check),
                                 ({0, 1},          add)))


