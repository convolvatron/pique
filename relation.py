from typing import *
from dataclasses import dataclass

@dataclass(frozen=True)
class Variable:
    name :str
        
    def __hash__(self):
        return self.name.__hash__()
    
    def __eq__(self, a):
        return self.name == a
    

Frame = Dict[str, Any]
Name = str
Constant  = Union[int, str]
# not str?
Argument = Union[Variable, Constant]
Term = List[Argument]
ArgSet = FrozenSet[Union[int, Name]]
Stream = Callable[[Frame, OutStream], None]
OutStream = Callable[[Frame], None]
Clause = Tuple[Argument, Dict[Variable, Argument]]
GeneratorResult = Union[Stream, None]
Genenrator = Callable[[Argset], GeneratorResult]

def is_constant(a) -> bool:
    return isinstance(a, get_args(Constant))

def fixed_handlers(h:List[Tuple[Argset, Stream]]) -> Generator:
    handlers = {}
    for i in h:
        handlers[i[0]] = i[1]
    return lambda a: handlers[a] if a in handlers else None

def positional_and_keyword(terms:List[Name]) -> Generator:
    def gen(a:Argset) -> GeneratorResult:
        
        return {frozenset(('k', 1))}

class Relation:
    arguments:List[Variable]
    
    def signature(self, b :ArgSet) -> Stream:
        print ("sig", b)
        if b not in self.cache:
            self.cache[b] = self.build(b)
        return self.cache[b]

    def __init__(self):
        self.cache :Dict[ArgSet, Stream] = {}            

class Aggregate(Relation):
    def signature(self, b :ArgSet) -> Stream:
        def entry(f: Frame):
            # demux arguments and flush
            pass
        pass
    def __init__(self):
        self.cache :Dict[ArgSet, Stream] = {}
        
class Simple(Relation):
    def __init__(self, *handlers):
        self.handlers = handlers
    
    def signature(self, b :ArgSet) -> Stream:
        def entry(f: Frame):
            # demux arguments and flush
            pass
        return entry

    
    
# supporting the implicit union for the moment..maybe more decorator magic
RelationSet = Dict[str, List[Relation]]

def format_clauses(cs:List[Clause])->str:
    col_width = max(len(word) for c in cs for word in c) + 2
    result = ""
    for c in cs:
        result += "".join(word.ljust(col_width) for word in c)
    return result
            

