from relation import *
from typing import *


# fully bound signatures are treated specially :( to make integration easier
def map_check(map, key, value) -> Iterable[Any]:
    pass

def map_iterate(map) -> Iterable[Any]:
    pass

def map_lookup(map, key) -> Iterable[Any]:
    pass

class Map(Relation):
    arguments = ['value', 1]

    fixed_handlers(({'map'}, map_iterate),
                   ({'map', 'key'}, map_lookup),
                   ({'map', 'key', 'value'}, map_check)),

class build_map(Aggregate):
    def __init__(self):
        self.map = {}
    def each(bindings):
        self.map[bindings[0]] = bindings[1]
    def flush(next):
        next(self.map)
