from typing import *
from relation import *

# infix results are always 'value'
# positional argumnets are integers
def add_check(f:Frame) -> Iterable[None]:
    pass

def add(a, b) -> Iterable[int]:
    return (a + b)

relation = Relation([0, 1],
                    fixed_handlers(({'value', 0, 1}, add_check),
                                   ({0, 1},          add)))


