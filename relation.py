from typing import *

Frame = Dict[str, Any]
Variable = str
ArgSet = FrozenSet[Variable]
# this is apparently the model for defining recursive types, using the namespace for the back edge(?)
# I would like this to be in translate, but relation.generate_signature uses it
Stream = Callable[[Frame], None]

# relation entry points take a dynamic next so we can share them between call sites
RelationStream = Callable[[Frame, 'Stream'], None]

# args is a list of (frozen(ArgSet), Stream) pairs
def fixed_handlers(*args):
    return {frozenset(('k', 1))}

# this doesn't handle cycles in ungenerated relation references - its just keeps trying to build them
def signature_cache(create: Callable[[ArgSet], Stream]) -> Callable[[ArgSet], RelationStream]:
    cache: Dict[ArgSet, Stream] = {}            
    # are ArgSet always in order? does set comparison work properly if they aren't? i guess so     
    def lookup(a :ArgSet):
        if a not in cache:
            cache[a] = create(a)
        return cache[a]
    return lookup

class Relation:
    def __init__(self, arguments:List[str], generate: Callable[[ArgSet], RelationStream]):
        self.generate_signature = generate
        self.arguments = arguments
    generate_signature: Callable[[ArgSet], RelationStream]
    arguments: ArgSet
    

