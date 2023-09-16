from relation import *
from typing import *


# fully bound signatures are treated specially :( to make integration easier
def map_check(map, key, value) -> Iterable[Any]:
    pass

def map_iterate(map) -> Iterable[Any]:
    pass

def map_lookup(map, key) -> Any:
    pass

# would we could do this implicitly on import, which would be nice, but
# relations would have to be a global
# I guess we could write a loader for this
# and an annotation

relation = Relation(
    fixed_handlers(({'map'}, map_iterate),
                   ({'map', 'key'}, map_lookup),
                   ({'map', 'key', 'value'}, map_check)),
    ['map', 'key', 'value'])
    
