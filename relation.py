from typing import *

class Variable:
    name :str
    def __init__(self, name):
        self.name = name
    

Frame = Dict[str, Any]
# or constant! - we have the same issue we've had before, variable vs constant string, but
# there is at least a syntactic distinciton
Referent = Union[str, int, Variable]
Term = List[Referent]
ArgSet = FrozenSet[Variable]
# this is apparently the model for defining recursive types, using the namespace for the back edge(?)
# I would like this to be in translate, but relation.generate_signature uses it
Stream = Callable[[Frame], None]

# relation entry points take a dynamic next so we can share them between call sites
RelationStream = Callable[[Frame, 'Stream'], None]

#clause is a one element of a horn clause conjunction...sorry
#should we add the constraint that the relation slot be a constant?
Clause = List[Term]

def is_constant(a) -> bool:
    return isinstance(a, int) or isinstance(a, str)

# args is a list of (frozen(ArgSet), Stream) pairs
def fixed_handlers(*args):
    return {frozenset(('k', 1))}

class Relation:
    arguments:List[Variable]
    
    def signature(self, b :ArgSet) -> RelationStream:
        if b not in self.cache:
            self.cache[b] = self.build(b)
        return self.cache[b]

    def __init__(self):
        self.cache :Dict[ArgSet, Stream] = {}            

# supporting the implicit union for the moment..maybe more decorator magic
RelationSet = Dict[str, List[Relation]]

def format_clauses(cs:List[Clause])->str:
    col_width = max(len(word) for c in cs for word in c) + 2
    result = ""
    for c in cs:
        result += "".join(word.ljust(col_width) for word in c)
    return result
            
